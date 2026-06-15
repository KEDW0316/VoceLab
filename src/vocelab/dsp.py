"""순수 신호 처리 헬퍼 (numpy만 의존, Qt/하드웨어 비의존).

UI·분석 양쪽에서 재사용하며 단위 테스트가 쉽도록 분리한다.
"""

from __future__ import annotations

import numpy as np


def envelope_downsample(
    mono: np.ndarray, samplerate: int, max_points: int = 4000
) -> tuple[np.ndarray, np.ndarray]:
    """min/max 엔벨로프로 파형을 다운샘플해 (x_seconds, y)를 반환한다.

    긴 녹음을 픽셀 수준으로 줄여 가볍게 렌더링하면서 피크 모양은 유지한다.
    """
    n = len(mono)
    if n <= max_points:
        x = np.arange(n) / samplerate
        return x, mono

    bucket = n // (max_points // 2)
    usable = (n // bucket) * bucket
    reshaped = mono[:usable].reshape(-1, bucket)
    mins = reshaped.min(axis=1)
    maxs = reshaped.max(axis=1)

    # min/max를 번갈아 배치해 엔벨로프 모양 유지
    y = np.empty(mins.size * 2, dtype=mono.dtype)
    y[0::2] = mins
    y[1::2] = maxs
    idx = np.repeat(np.arange(mins.size) * bucket, 2)
    x = idx / samplerate
    return x, y


def spectrogram_db(
    mono: np.ndarray,
    samplerate: int,
    *,
    nperseg: int = 1024,
    overlap: float = 0.75,
    fmax: float = 5000.0,
    floor_db: float = -90.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """로그(dB) 파워 스펙트로그램을 계산해 (times, freqs, db)를 반환한다.

    db는 (n_freqs, n_times) 배열로, 최댓값을 0 dB로 정규화하고 floor_db에서 클립한다.
    scipy만 사용(순수 함수)하여 단위 테스트가 쉽다.
    """
    from scipy.signal import spectrogram as _spec

    if mono.size < nperseg:
        nperseg = max(64, 1 << int(np.floor(np.log2(max(mono.size, 64)))))
    noverlap = int(nperseg * overlap)

    freqs, times, sxx = _spec(
        mono.astype(np.float64),
        fs=samplerate,
        nperseg=nperseg,
        noverlap=noverlap,
        scaling="spectrum",
        mode="magnitude",
    )

    if fmax:
        keep = freqs <= fmax
        freqs = freqs[keep]
        sxx = sxx[keep, :]

    db = 20.0 * np.log10(sxx + 1e-12)
    db -= db.max()  # 0 dB로 정규화
    np.clip(db, floor_db, 0.0, out=db)
    return times, freqs, db


def spectrum(
    mono: np.ndarray,
    samplerate: int,
    *,
    fmin: float = 50.0,
    fmax: float = 16000.0,
    n_out: int = 180,
    floor_db: float = -100.0,
) -> tuple[list[float], list[float]]:
    """실시간 스펙트럼 분석기(EQ 곡선)용 단일 프레임 크기 스펙트럼.

    최근 오디오 한 프레임의 rFFT 크기를 **절대 dBFS**로 변환한다(프레임별 정규화 X).
    풀스케일 사인(진폭 1)의 피크가 ≈0 dBFS가 되도록 기준화하므로, 잡소리는 바닥에
    깔리고 축이 고정된다. 로그 주파수 축으로 n_out개 지점에 보간해 (freqs, db)를 반환.
    """
    mono = np.asarray(mono, dtype=np.float64)
    if mono.size < 256:
        return [], []

    n = min(4096, len(mono))
    window = np.hanning(n)
    seg = mono[-n:] * window
    mag = np.abs(np.fft.rfft(seg))
    freqs = np.fft.rfftfreq(n, d=1.0 / samplerate)

    # 절대 dBFS: Hann 창에서 풀스케일 사인 피크 ≈ N/4
    ref = n / 4.0
    db = 20.0 * np.log10(mag / ref + 1e-12)
    np.clip(db, floor_db, 6.0, out=db)

    keep = (freqs >= fmin) & (freqs <= fmax)
    if not keep.any():
        return [], []
    f, d = freqs[keep], db[keep]

    target = np.logspace(np.log10(fmin), np.log10(min(fmax, f[-1])), n_out)
    interp = np.interp(target, f, d)
    return [round(float(x), 1) for x in target], [round(float(y), 1) for y in interp]


# --- 장기 평균 스펙트럼(LTAS) 기반 밴드 측정 --------------------------------


def ltas(mono: np.ndarray, samplerate: int, *, nperseg: int = 2048) -> tuple[np.ndarray, np.ndarray]:
    """Welch 평균 파워 스펙트럼을 계산해 (freqs, power)를 반환한다.

    공명·음색 관련 밴드 측정(Alpha ratio, Hammarberg, SPR)의 공통 기반.
    """
    from scipy.signal import welch

    n = min(nperseg, len(mono))
    n = max(64, 1 << int(np.floor(np.log2(max(n, 64)))))
    freqs, power = welch(mono.astype(np.float64), fs=samplerate, nperseg=n)
    return freqs, power


def _band_sum(freqs, power, lo, hi) -> float:
    mask = (freqs >= lo) & (freqs < hi)
    return float(power[mask].sum()) if mask.any() else 0.0


def _band_max(freqs, power, lo, hi) -> float:
    mask = (freqs >= lo) & (freqs < hi)
    return float(power[mask].max()) if mask.any() else 0.0


def _safe_db(ratio: float) -> float | None:
    if ratio <= 0:
        return None
    return 10.0 * np.log10(ratio)


def alpha_ratio(freqs: np.ndarray, power: np.ndarray) -> float | None:
    """Alpha ratio (dB) = 1–5 kHz 에너지 / 50 Hz–1 kHz 에너지.

    발성 노력·음색의 밝기. 값이 높을수록(덜 음수) 고역 에너지가 풍부.
    """
    low = _band_sum(freqs, power, 50, 1000)
    high = _band_sum(freqs, power, 1000, 5000)
    return _safe_db(high / low) if low > 0 else None


def hammarberg_index(freqs: np.ndarray, power: np.ndarray) -> float | None:
    """Hammarberg index (dB) = 0–2 kHz 최대 − 2–5 kHz 최대.

    저역 대비 고역 피크 차이. 값이 클수록 고역 에너지가 상대적으로 약함.
    """
    low = _band_max(freqs, power, 0, 2000)
    high = _band_max(freqs, power, 2000, 5000)
    return _safe_db(low / high) if high > 0 else None


def singing_power_ratio(freqs: np.ndarray, power: np.ndarray) -> float | None:
    """SPR (dB) = 0–2 kHz 최대 피크 − 2–4 kHz 최대 피크.

    Singer's Formant(성악적 울림, ~2.8–3.4 kHz) 지표. 값이 **낮을수록**
    2–4 kHz 공명이 강해 또렷한 '링'이 있는 발성.
    """
    low = _band_max(freqs, power, 0, 2000)
    high = _band_max(freqs, power, 2000, 4000)
    return _safe_db(low / high) if high > 0 else None


# --- 비브라토 분석 -----------------------------------------------------------


def vibrato_from_contour(
    f0_hz: np.ndarray, dt: float
) -> tuple[float | None, float | None]:
    """F0 컨투어에서 비브라토 (rate_Hz, extent_semitones)를 추정한다.

    f0_hz: 균일 시간 간격(dt초)의 기본주파수 배열. 무성 구간은 0 또는 NaN.
    반환: (비브라토 주기[Hz], 진폭[반음, peak-to-peak]). 추정 불가 시 (None, None).

    절차: 유성 최장 구간 → 반음 변환 → 추세 제거 → FFT로 3–9 Hz 대역 피크를
    찾아 rate, 정현파 가정으로 extent(peak-to-peak)를 산출.
    """
    f0 = np.asarray(f0_hz, dtype=np.float64).copy()
    f0[f0 <= 0] = np.nan

    voiced = ~np.isnan(f0)
    if voiced.sum() < 8:
        return None, None

    # 가장 긴 연속 유성 구간 선택
    start, length = _longest_true_run(voiced)
    if length * dt < 0.3:  # 0.3초 미만이면 비브라토 추정 불가
        return None, None
    seg = f0[start : start + length]

    # 반음(semitone) 변환. 드리프트 제거는 아래 FFT 밴드패스(3–9 Hz)가 담당하므로
    # 별도 이동평균 추세제거는 하지 않는다(이동평균은 비브라토 성분을 왜곡함).
    semitones = 12.0 * np.log2(seg / np.nanmedian(seg))

    # FFT로 3–9 Hz 대역의 주된 진동수 탐색 (rate)
    n = semitones.size
    window = np.hanning(n)
    spec = np.abs(np.fft.rfft(semitones * window))
    fft_freqs = np.fft.rfftfreq(n, d=dt)
    band = (fft_freqs >= 3.0) & (fft_freqs <= 9.0)
    if not band.any() or spec[band].max() <= 0:
        return None, None

    band_idx = np.flatnonzero(band)
    rate = float(fft_freqs[band_idx[np.argmax(spec[band])]])

    # extent는 비브라토 대역만 FFT 밴드패스로 분리한 뒤 산출한다.
    # 저주파 드리프트와 고주파 피치 추적 노이즈가 제거되어,
    # 정현파 가정(peak-to-peak = 2*sqrt(2)*RMS)이 잘 성립한다.
    spec_raw = np.fft.rfft(semitones)
    spec_raw[~band] = 0.0
    filtered = np.fft.irfft(spec_raw, n=n)
    extent = float(2.0 * np.sqrt(2.0) * np.std(filtered))
    return rate, extent


def _longest_true_run(mask: np.ndarray) -> tuple[int, int]:
    """불리언 배열에서 가장 긴 True 연속 구간의 (시작, 길이)."""
    best_start = best_len = 0
    cur_start = cur_len = 0
    for i, v in enumerate(mask):
        if v:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len, best_start = cur_len, cur_start
        else:
            cur_len = 0
    return best_start, best_len
