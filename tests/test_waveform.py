"""파형 다운샘플 로직 테스트 (Qt/하드웨어 불필요)."""

import numpy as np

from vocelab.dsp import envelope_downsample


def test_downsample_short_signal_passthrough():
    sig = np.linspace(-1, 1, 100, dtype="float32")
    x, y = envelope_downsample(sig, samplerate=100, max_points=4000)
    assert len(x) == len(y) == 100
    assert x[0] == 0.0
    assert np.isclose(x[-1], 99 / 100)


def test_downsample_long_signal_reduced():
    sig = np.sin(np.linspace(0, 100, 100_000)).astype("float32")
    x, y = envelope_downsample(sig, samplerate=44100, max_points=4000)
    assert len(x) == len(y)
    assert len(x) <= 4000 + 2
    # 엔벨로프는 원신호 범위를 벗어나지 않음
    assert y.min() >= sig.min() - 1e-6
    assert y.max() <= sig.max() + 1e-6
