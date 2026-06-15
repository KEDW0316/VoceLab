"""AudioEngine 재생/녹음 배선 테스트 (sounddevice를 가짜로 주입, 하드웨어 불필요)."""

import sys
import types

import numpy as np
import pytest

from vocelab.audio.engine import AudioEngine


class FakeSD:
    """sounddevice 대역 — 호출 인자를 기록한다."""

    def __init__(self):
        self.play_calls = []
        self.stop_calls = 0

    def play(self, data, samplerate=None, device=None, loop=False):
        self.play_calls.append({"len": len(data), "loop": loop, "device": device})

    def stop(self):
        self.stop_calls += 1


@pytest.fixture
def fake_sd(monkeypatch):
    fake = FakeSD()
    module = types.ModuleType("sounddevice")
    module.play = fake.play
    module.stop = fake.stop
    monkeypatch.setitem(sys.modules, "sounddevice", module)
    return fake


def test_play_passes_loop_false_by_default(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((1000, 1), dtype="float32")
    eng.play()
    assert fake_sd.play_calls[-1]["loop"] is False


def test_play_loop_true_forwarded(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((1000, 1), dtype="float32")
    eng.play(loop=True)
    assert fake_sd.play_calls[-1]["loop"] is True


def test_play_noop_on_empty_buffer(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((0, 1), dtype="float32")
    eng.play()
    assert fake_sd.play_calls == []


def test_stop_playback_calls_sd_stop(fake_sd):
    eng = AudioEngine()
    eng.stop_playback()
    assert fake_sd.stop_calls == 1
