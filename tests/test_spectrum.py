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
