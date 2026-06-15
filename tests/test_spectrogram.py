"""스펙트로그램 계산 테스트 (scipy만, Qt/하드웨어 불필요)."""

import numpy as np

from vocelab.dsp import spectrogram_db


def test_spectrogram_shapes_and_range():
    sr = 44100
    t = np.arange(sr) / sr  # 1초
    sig = np.sin(2 * np.pi * 1000 * t).astype("float32")
    times, freqs, db = spectrogram_db(sig, sr, fmax=5000)

    assert db.shape == (freqs.size, times.size)
    assert freqs.max() <= 5000
    # 0 dB로 정규화되고 floor에서 클립
    assert np.isclose(db.max(), 0.0, atol=1e-6)
    assert db.min() >= -90.0 - 1e-6


def test_spectrogram_peak_at_tone_frequency():
    sr = 44100
    t = np.arange(sr) / sr
    sig = np.sin(2 * np.pi * 1000 * t).astype("float32")
    _, freqs, db = spectrogram_db(sig, sr)
    # 시간 평균 스펙트럼의 피크가 1000Hz 근처여야 함
    mean_spectrum = db.mean(axis=1)
    peak_freq = freqs[np.argmax(mean_spectrum)]
    assert abs(peak_freq - 1000) < 100


def test_spectrogram_handles_short_signal():
    sr = 44100
    sig = np.random.randn(300).astype("float32")
    times, freqs, db = spectrogram_db(sig, sr)
    assert db.shape == (freqs.size, times.size)
