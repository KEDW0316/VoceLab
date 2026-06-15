"""지표 해석(rating) 테스트."""

from vocelab.analysis.rating import GOOD, INFO, POOR, WATCH, rate


def test_high_better_cpps():
    assert rate("cpps", 8.0)[0] == GOOD
    assert rate("cpps", 3.0)[0] == WATCH
    assert rate("cpps", 1.0)[0] == POOR


def test_low_better_jitter():
    assert rate("jitter", 0.5)[0] == GOOD
    assert rate("jitter", 1.5)[0] == WATCH
    assert rate("jitter", 3.0)[0] == POOR


def test_band_vibrato_rate():
    assert rate("vibrato_rate", 5.5)[0] == GOOD
    assert rate("vibrato_rate", 7.5)[0] == WATCH
    assert rate("vibrato_rate", 10.0)[0] == POOR


def test_info_for_unrated_and_none():
    assert rate("f1", 500.0) == (INFO, "")
    assert rate("alpha", -11.0) == (INFO, "")
    assert rate("cpps", None) == (INFO, "")


def test_note_present_for_rated():
    status, note = rate("hnr", 25.0)
    assert status == GOOD and note != ""
