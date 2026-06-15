"""공명 밴드 측정 및 비브라토 추정 테스트 (순수 DSP, 하드웨어 불필요)."""

import numpy as np

from vocelab.dsp import (
    alpha_ratio,
    hammarberg_index,
    ltas,
    singing_power_ratio,
    vibrato_from_contour,
)

SR = 44100


def _tone(freqs_amps, dur=1.0):
    t = np.arange(int(SR * dur)) / SR
    sig = np.zeros_like(t)
    for f, a in freqs_amps:
        sig += a * np.sin(2 * np.pi * f * t)
    return sig.astype("float64")


def test_ring_has_lower_spr_than_dull():
    """3kHz 공명이 있는 신호가 없는 신호보다 SPR이 낮아야 한다."""
    ring = _tone([(220, 1.0), (440, 0.5), (3000, 0.6)])
    dull = _tone([(220, 1.0), (440, 0.5)])
    f_r, p_r = ltas(ring, SR)
    f_d, p_d = ltas(dull, SR)
    assert singing_power_ratio(f_r, p_r) < singing_power_ratio(f_d, p_d)


def test_alpha_ratio_higher_with_high_freq_energy():
    bright = _tone([(220, 1.0), (3000, 0.8)])
    dark = _tone([(220, 1.0), (330, 0.3)])
    f_b, p_b = ltas(bright, SR)
    f_d, p_d = ltas(dark, SR)
    assert alpha_ratio(f_b, p_b) > alpha_ratio(f_d, p_d)


def test_hammarberg_defined_for_normal_signal():
    sig = _tone([(220, 1.0), (440, 0.5), (3000, 0.4)])
    f, p = ltas(sig, SR)
    assert hammarberg_index(f, p) is not None


def test_vibrato_rate_and_extent_recovered():
    dt = 0.01
    tt = np.arange(0, 1.5, dt)
    semis = 0.5 * np.sin(2 * np.pi * 5.5 * tt)  # ±0.5 반음 → p2p ~1.0
    f0 = 220 * 2 ** (semis / 12)
    rate, extent = vibrato_from_contour(f0, dt)
    assert rate is not None and abs(rate - 5.5) < 0.6
    assert extent is not None and 0.7 < extent < 1.6


def test_vibrato_none_for_steady_tone():
    rate, extent = vibrato_from_contour(np.full(150, 220.0), 0.01)
    assert rate is None and extent is None


def test_vibrato_none_for_too_short_contour():
    rate, extent = vibrato_from_contour(np.full(5, 220.0), 0.01)
    assert rate is None and extent is None
