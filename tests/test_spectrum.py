"""실시간 스펙트럼(분석기) 테스트 — dsp.spectrum + 엔진 링버퍼 + webapp."""

import numpy as np

from vocelab.audio.engine import AudioEngine
from vocelab.dsp import spectrum
from vocelab.webapp import Api

SR = 44100


def test_spectrum_peak_at_tone():
    t = np.arange(SR) / SR
    sig = np.sin(2 * np.pi * 1000 * t).astype("float32")
    freqs, db = spectrum(sig, SR)
    assert len(freqs) == len(db) > 0
    # 0 dB 정규화 후 로그 보간이라 피크는 0에 근접(정확히 0은 아닐 수 있음)
    assert max(db) > -6.0
    peak_freq = freqs[int(np.argmax(db))]
    assert abs(peak_freq - 1000) < 150


def test_spectrum_log_frequency_increasing():
    t = np.arange(SR) / SR
    freqs, _ = spectrum(np.sin(2 * np.pi * 440 * t).astype("float32"), SR)
    assert all(freqs[i] < freqs[i + 1] for i in range(len(freqs) - 1))
    assert freqs[0] >= 50 and freqs[-1] <= 16000


def test_spectrum_empty_for_tiny_input():
    assert spectrum(np.zeros(10, dtype="float32"), SR) == ([], [])


def test_engine_recent_ringbuffer():
    eng = AudioEngine()
    eng._recent_max = 100
    for _ in range(5):
        eng._push_recent(np.ones(30, dtype="float32"))
    assert eng.recent_samples().size == 100  # 30*5=150 → 최근 100만 유지


def test_api_get_spectrum_shape(monkeypatch):
    api = Api()
    t = np.arange(4096) / SR
    monkeypatch.setattr(
        api.engine, "recent_samples", lambda: np.sin(2 * np.pi * 800 * t).astype("float32")
    )
    out = api.get_spectrum()
    assert set(out) == {"freqs", "db"}
    assert len(out["freqs"]) == len(out["db"]) > 0


def test_api_get_spectrum_empty_when_no_audio(monkeypatch):
    api = Api()
    monkeypatch.setattr(api.engine, "recent_samples", lambda: np.zeros(0, dtype="float32"))
    assert api.get_spectrum() == {"freqs": [], "db": []}


# ---- 실시간 음정 검출 ----------------------------------------------------
from vocelab.dsp import detect_pitch
from vocelab.synth import freq_to_note


def test_detect_pitch_on_tone():
    t = np.arange(SR) / SR
    sig = (0.5 * np.sin(2 * np.pi * 220 * t)).astype("float32")
    f0 = detect_pitch(sig, SR)
    assert f0 is not None and abs(f0 - 220) < 3


def test_detect_pitch_silence_returns_none():
    assert detect_pitch(np.zeros(4096, dtype="float32"), SR) is None


def test_detect_pitch_voiced_male_range():
    t = np.arange(SR) / SR
    sig = (0.4 * np.sin(2 * np.pi * 110 * t) + 0.2 * np.sin(2 * np.pi * 220 * t)).astype("float32")
    f0 = detect_pitch(sig, SR)
    assert f0 is not None and abs(f0 - 110) < 3


def test_freq_to_note_a4():
    name, octave, cents = freq_to_note(440.0)
    assert name == "A" and octave == 4 and abs(cents) <= 1


def test_freq_to_note_c4_and_cents():
    name, octave, _ = freq_to_note(261.63)
    assert name == "C" and octave == 4
    # 약간 높은 A4 → +cents
    _, _, cents = freq_to_note(444.0)
    assert cents > 0


def test_api_get_pitch_praat(monkeypatch):
    from vocelab.webapp import Api
    api = Api()
    t = np.arange(8192) / SR
    sig = (0.5 * np.sin(2 * np.pi * 220 * t)).astype("float32")  # 220Hz = A3
    monkeypatch.setattr(api.engine, "recent_samples", lambda: sig)
    out = api.get_pitch()
    assert out["hz"] is not None and abs(out["hz"] - 220) < 4
    assert out["note"] == "A" and out["octave"] == 3


# ---- 대표 구간 선택 ------------------------------------------------------
from vocelab.dsp import representative_window


def test_representative_window_short_passthrough():
    sig = np.ones(SR, dtype="float32")  # 1초
    assert representative_window(sig, SR, max_sec=12).size == SR


def test_representative_window_picks_loud_segment():
    # 30초: 앞뒤 조용, 중앙 5초만 큰 소리 → 대표구간이 그 큰 부분을 포함
    n = 30 * SR
    sig = (0.001 * np.random.randn(n)).astype("float64")
    lo, hi = 12 * SR, 17 * SR
    sig[lo:hi] += 0.5 * np.sin(2 * np.pi * 220 * np.arange(hi - lo) / SR)
    seg = representative_window(sig, SR, max_sec=8)
    assert seg.size == 8 * SR
    # 대표구간 RMS가 전체 RMS보다 확실히 큼(조용한 부분 회피)
    assert np.sqrt(np.mean(seg**2)) > np.sqrt(np.mean(sig**2))
