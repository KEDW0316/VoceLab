"""Praat(Parselmouth) 기반 음향 지표 산출. (M2)

녹음 버퍼(numpy)를 받아 보컬 트레이닝에 유의미한 음향 지표를 계산한다.
핵심은 CPPS(요구 3)이며, 같은 Sound 객체에서 함께 얻을 수 있는 HNR·F0·
지터·쉬머도 제공한다(요구 4의 시작).

각 지표는 값/단위/설명/정상참고범위를 담은 `Metric`으로 표준화한다. 무성음·
너무 짧은 구간 등으로 Praat이 정의불가(undefined)를 반환하면 value=None으로
처리하여 UI가 "—"로 표시할 수 있게 한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    value: float | None
    unit: str
    description: str
    normal: str = ""  # 정상/참고 범위 안내 (선택)
    category: str = "기타"  # 패널 그룹핑용

    @property
    def display(self) -> str:
        if self.value is None or (isinstance(self.value, float) and math.isnan(self.value)):
            return "—"
        return f"{self.value:.2f}"


@dataclass(frozen=True)
class VoiceMetrics:
    metrics: list[Metric]

    def get(self, key: str) -> Metric | None:
        for m in self.metrics:
            if m.key == key:
                return m
        return None


# F0 탐색 범위 (일반 성인 음성). 추후 사용자/성별별 조정 가능.
F0_FLOOR = 75.0
F0_CEILING = 600.0


def to_mono_f64(samples: np.ndarray) -> np.ndarray:
    """(frames, channels) 또는 1D 버퍼를 float64 모노로 변환.

    멀티채널이면 첫 채널(보통 마이크가 꽂힌 입력 1)을 사용한다.
    """
    arr = np.asarray(samples)
    if arr.ndim == 2:
        arr = arr[:, 0]
    return np.ascontiguousarray(arr, dtype=np.float64)


def _clean(value: float) -> float | None:
    """Praat의 undefined(NaN/inf)를 None으로 정규화."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def analyze(samples: np.ndarray, samplerate: int) -> VoiceMetrics:
    """녹음 버퍼에서 음향 지표를 계산해 VoiceMetrics로 반환.

    Parselmouth는 지연 import 한다(미설치 환경에서도 모듈 로드 가능).
    개별 지표 계산이 실패해도 전체가 중단되지 않도록 각자 예외를 격리한다.
    """
    import parselmouth as pm
    from parselmouth.praat import call

    mono = to_mono_f64(samples)
    metrics: list[Metric] = []

    def add(key, label, value, unit, desc, normal=""):
        metrics.append(
            Metric(key, label, _clean(value), unit, desc, normal, _CATEGORIES.get(key, "기타"))
        )

    # 신호가 너무 짧으면 분석 불가 — 전부 None
    if mono.size < samplerate * 0.05:  # 50ms 미만
        for key, label, unit, desc, normal in _METRIC_SPEC:
            add(key, label, None, unit, desc, normal)
        return VoiceMetrics(metrics)

    snd = pm.Sound(mono, sampling_frequency=samplerate)

    # --- CPPS (핵심 지표, 요구 3) -------------------------------------------
    cpps = None
    try:
        pcg = call(snd, "To PowerCepstrogram", 60, 0.002, 5000, 50)
        cpps = call(
            pcg, "Get CPPS", False, 0.02, 0.0005, 60, 330, 0.05,
            "parabolic", 0.001, 0, "Exponential decay", "Robust",
        )
    except Exception:  # noqa: BLE001
        cpps = None
    add(
        "cpps", "CPPS", cpps, "dB",
        "Cepstral Peak Prominence (Smoothed). 음질의 핵심 지표 — 높을수록 또렷하고 "
        "규칙적인 발성, 낮을수록 기식성/거친 음질.",
        normal="대략 ≥ 4 dB 권장 (모음 지속발성 기준)",
    )

    # --- HNR -----------------------------------------------------------------
    hnr = None
    try:
        harm = call(snd, "To Harmonicity (cc)", 0.01, F0_FLOOR, 0.1, 1.0)
        hnr = call(harm, "Get mean", 0, 0)
    except Exception:  # noqa: BLE001
        hnr = None
    add(
        "hnr", "HNR", hnr, "dB",
        "Harmonics-to-Noise Ratio. 배음 대비 잡음 비율 — 높을수록 깨끗한 발성.",
        normal="건강한 모음 발성에서 보통 ≥ 20 dB",
    )

    # --- F0 (평균/표준편차) ---------------------------------------------------
    f0_mean = f0_sd = None
    pitch = None
    try:
        pitch = call(snd, "To Pitch", 0.0, F0_FLOOR, F0_CEILING)
        f0_mean = call(pitch, "Get mean", 0, 0, "Hertz")
        f0_sd = call(pitch, "Get standard deviation", 0, 0, "Hertz")
    except Exception:  # noqa: BLE001
        pitch = None
    add(
        "f0_mean", "평균 F0", f0_mean, "Hz",
        "기본 주파수(음높이)의 평균.",
    )
    add(
        "f0_sd", "F0 표준편차", f0_sd, "Hz",
        "음높이의 흔들림 정도. 지속발성에서는 낮을수록 안정적.",
    )

    # --- 지터 / 쉬머 ----------------------------------------------------------
    jitter = shimmer = None
    try:
        pp = call(snd, "To PointProcess (periodic, cc)", F0_FLOOR, F0_CEILING)
        jitter = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        shimmer = call(
            [snd, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6
        )
    except Exception:  # noqa: BLE001
        pass
    # Praat은 비율(0~1)로 반환 → %로 환산
    add(
        "jitter", "Jitter (local)",
        None if jitter is None else jitter * 100.0, "%",
        "주기 간 주파수 섭동. 성대 진동의 규칙성 — 낮을수록 안정적.",
        normal="보통 < 1%",
    )
    add(
        "shimmer", "Shimmer (local)",
        None if shimmer is None else shimmer * 100.0, "%",
        "주기 간 진폭 섭동. 음량의 규칙성 — 낮을수록 안정적.",
        normal="보통 < 3.8%",
    )

    # --- 포먼트 (F1~F3) ------------------------------------------------------
    f1 = f2 = f3 = None
    try:
        fm = call(snd, "To Formant (burg)", 0.0, 5, 5500, 0.025, 50)
        f1 = call(fm, "Get mean", 1, 0, 0, "Hertz")
        f2 = call(fm, "Get mean", 2, 0, 0, "Hertz")
        f3 = call(fm, "Get mean", 3, 0, 0, "Hertz")
    except Exception:  # noqa: BLE001
        pass
    add("f1", "F1", f1, "Hz", "제1 포먼트. 모음의 개구도(입 벌림)와 관련.")
    add("f2", "F2", f2, "Hz", "제2 포먼트. 혀의 전후 위치(모음 색)와 관련.")
    add("f3", "F3", f3, "Hz", "제3 포먼트. 음색/공명에 기여.")

    # --- 공명·음색 (스펙트럼 밴드 측정) --------------------------------------
    from vocelab.dsp import alpha_ratio, hammarberg_index, ltas, singing_power_ratio

    try:
        freqs, power = ltas(mono, samplerate)
        add(
            "alpha", "Alpha ratio", alpha_ratio(freqs, power), "dB",
            "고역(1–5kHz) 대 저역(50Hz–1kHz) 에너지 비. 높을수록(덜 음수) 밝고 "
            "에너지 있는 음색.",
        )
        add(
            "hammarberg", "Hammarberg", hammarberg_index(freqs, power), "dB",
            "0–2kHz 최대 − 2–5kHz 최대. 작을수록 고역 공명이 풍부.",
        )
        add(
            "spr", "SPR", singing_power_ratio(freqs, power), "dB",
            "Singing Power Ratio. 낮을수록 2–4kHz의 Singer's Formant(성악적 '링') 강함.",
            normal="성악 발성에서 낮을수록 유리",
        )
    except Exception:  # noqa: BLE001
        add("alpha", "Alpha ratio", None, "dB", "고역 대 저역 에너지 비.")
        add("hammarberg", "Hammarberg", None, "dB", "저역 대 고역 피크 차.")
        add("spr", "SPR", None, "dB", "Singing Power Ratio.")

    # --- 비브라토 (F0 컨투어 기반) -------------------------------------------
    from vocelab.dsp import vibrato_from_contour

    v_rate = v_extent = None
    if pitch is not None:
        try:
            contour = pitch.selected_array["frequency"]
            v_rate, v_extent = vibrato_from_contour(contour, pitch.dt)
        except Exception:  # noqa: BLE001
            pass
    add(
        "vibrato_rate", "비브라토 rate", v_rate, "Hz",
        "비브라토의 주기. 노래에서 보통 4–7 Hz가 자연스럽다고 알려짐.",
        normal="대략 4–7 Hz",
    )
    add(
        "vibrato_extent", "비브라토 extent", v_extent, "반음",
        "비브라토의 폭(peak-to-peak). 보통 0.5–2 반음.",
        normal="대략 0.5–2 반음",
    )

    return VoiceMetrics(metrics)


_CATEGORIES = {
    "cpps": "음질",
    "hnr": "음질",
    "jitter": "음질",
    "shimmer": "음질",
    "f0_mean": "음높이",
    "f0_sd": "음높이",
    "f1": "공명·음색",
    "f2": "공명·음색",
    "f3": "공명·음색",
    "alpha": "공명·음색",
    "hammarberg": "공명·음색",
    "spr": "공명·음색",
    "vibrato_rate": "비브라토",
    "vibrato_extent": "비브라토",
}


# 짧은 신호 등으로 조기 반환할 때 사용할 지표 메타(순서/설명 일관성 유지)
_METRIC_SPEC = [
    ("cpps", "CPPS", "dB", "Cepstral Peak Prominence (Smoothed). 음질 핵심 지표.",
     "대략 ≥ 4 dB 권장"),
    ("hnr", "HNR", "dB", "Harmonics-to-Noise Ratio.", "보통 ≥ 20 dB"),
    ("f0_mean", "평균 F0", "Hz", "기본 주파수의 평균.", ""),
    ("f0_sd", "F0 표준편차", "Hz", "음높이의 흔들림 정도.", ""),
    ("jitter", "Jitter (local)", "%", "주기 간 주파수 섭동.", "보통 < 1%"),
    ("shimmer", "Shimmer (local)", "%", "주기 간 진폭 섭동.", "보통 < 3.8%"),
    ("f1", "F1", "Hz", "제1 포먼트.", ""),
    ("f2", "F2", "Hz", "제2 포먼트.", ""),
    ("f3", "F3", "Hz", "제3 포먼트.", ""),
    ("alpha", "Alpha ratio", "dB", "고역 대 저역 에너지 비.", ""),
    ("hammarberg", "Hammarberg", "dB", "저역 대 고역 피크 차.", ""),
    ("spr", "SPR", "dB", "Singing Power Ratio.", ""),
    ("vibrato_rate", "비브라토 rate", "Hz", "비브라토 주기.", "대략 4–7 Hz"),
    ("vibrato_extent", "비브라토 extent", "반음", "비브라토 폭.", "대략 0.5–2 반음"),
]
