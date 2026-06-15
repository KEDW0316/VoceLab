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


def test_includes_m3_metrics_with_categories():
    vm = analyze(_vowel(noise=0.0), SR)
    # 포먼트·공명·비브라토 지표가 추가됨
    for key in ("f1", "f2", "f3", "alpha", "hammarberg", "spr",
                "vibrato_rate", "vibrato_extent"):
        assert vm.get(key) is not None, f"missing {key}"
    assert vm.get("cpps").category == "음질"
    assert vm.get("f1").category == "공명·음색"
    assert vm.get("vibrato_rate").category == "비브라토"


def test_formants_are_positive():
    vm = analyze(_vowel(f0=150.0), SR)
    f1 = vm.get("f1").value
    assert f1 is not None and f1 > 0


def test_short_signal_metric_count_matches_full():
    """짧은 신호도 전체와 동일한 지표 집합을 반환해야 한다(일관성)."""
    full = analyze(_vowel(noise=0.0), SR)
    short = analyze(np.random.randn(441).astype("float32"), SR)
    assert {m.key for m in full.metrics} == {m.key for m in short.metrics}
