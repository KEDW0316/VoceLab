"""음향 지표 산출 테스트 (Parselmouth, 합성 신호 — 하드웨어 불필요)."""

import numpy as np
import pytest

from vocelab.analysis import analyze, to_mono_f64

pytest.importorskip("parselmouth")

SR = 44100


def _vowel(f0=220.0, dur=0.6, noise=0.0):
    t = np.arange(int(SR * dur)) / SR
    sig = (
        np.sin(2 * np.pi * f0 * t)
        + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)
        + 0.15 * np.sin(2 * np.pi * 3 * f0 * t)
    )
    if noise:
        sig = sig * (1 - noise) + noise * np.random.randn(t.size)
    return sig.astype("float32")


def test_to_mono_from_stereo():
    stereo = np.zeros((100, 2), dtype="float32")
    stereo[:, 0] = 1.0
    mono = to_mono_f64(stereo)
    assert mono.ndim == 1
    assert mono.dtype == np.float64
    assert np.all(mono == 1.0)


def test_f0_matches_synthesized_tone():
    vm = analyze(_vowel(f0=220.0), SR)
    f0 = vm.get("f0_mean")
    assert f0 is not None and f0.value is not None
    assert abs(f0.value - 220.0) < 5.0


def test_clean_tone_has_high_cpps_and_hnr():
    vm = analyze(_vowel(noise=0.0), SR)
    assert vm.get("cpps").value > 4.0
    assert vm.get("hnr").value > 20.0


def test_breathy_signal_has_lower_cpps_than_clean():
    clean = analyze(_vowel(noise=0.0), SR).get("cpps").value
    breathy = analyze(_vowel(noise=0.6), SR).get("cpps").value
    assert breathy < clean


def test_short_signal_returns_none_values():
    vm = analyze(np.random.randn(441).astype("float32"), SR)  # 10ms
    assert all(m.value is None for m in vm.metrics)
    # 메타데이터(라벨/단위)는 유지
    assert vm.get("cpps").label == "CPPS"
    assert vm.get("cpps").display == "—"
