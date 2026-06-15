"""가이드 톤 합성 + 스케일 라이브러리 테스트 (순수, 하드웨어 불필요)."""

import numpy as np
import pytest

from vocelab.scales import SCALES, SCALES_BY_KEY, get_scale
from vocelab.synth import (
    note_name_to_freq,
    note_name_to_midi,
    solfege,
    synthesize,
)

SR = 44100


def test_note_name_to_midi_and_freq():
    assert note_name_to_midi("C4") == 60
    assert note_name_to_midi("A4") == 69
    assert abs(note_name_to_freq("A4") - 440.0) < 1e-6
    assert abs(note_name_to_freq("C4") - 261.63) < 0.05


def test_transpose_is_semitone_ratio():
    # 반음 위는 2^(1/12) 배
    assert abs(note_name_to_freq("C#4") / note_name_to_freq("C4") - 2 ** (1 / 12)) < 1e-6


def test_solfege_basic_major():
    assert solfege((0, 2, 4, 5, 7)) == "도 레 미 파 솔"


def test_synthesize_shape_and_no_clipping():
    for s in SCALES:
        buf = synthesize(s, 220.0, SR)
        assert buf.ndim == 2 and buf.shape[1] == 1, s.key
        assert len(buf) > 0, s.key
        assert np.abs(buf).max() <= 1.0, f"{s.key} clips"


def test_synthesized_first_note_matches_tonic():
    """5-tone의 첫 음 주파수가 토닉과 일치해야 한다."""
    buf = synthesize(get_scale("five_tone"), note_name_to_freq("C4"), SR)
    note0 = buf[: int(SR * 0.3), 0]
    freqs = np.fft.rfftfreq(note0.size, 1 / SR)
    spec = np.abs(np.fft.rfft(note0 * np.hanning(note0.size)))
    peak = freqs[np.argmax(spec)]
    assert abs(peak - note_name_to_freq("C4")) < 5.0


def test_glide_scale_is_continuous_length():
    siren = get_scale("siren")
    buf = synthesize(siren, 220.0, SR)
    assert abs(len(buf) / SR - siren.total_dur) < 0.05


def test_scale_library_integrity():
    assert len(SCALES) >= 8
    keys = [s.key for s in SCALES]
    assert len(keys) == len(set(keys)), "중복 key"
    assert set(SCALES_BY_KEY) == set(keys)
    for s in SCALES:
        assert s.name and s.description and s.syllable
        assert s.glide or len(s.pattern) >= 1


def test_get_scale_unknown_returns_none():
    assert get_scale("nope") is None
