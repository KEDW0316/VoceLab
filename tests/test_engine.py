"""AudioEngine 재생/녹음 배선 테스트 (sounddevice를 가짜로 주입, 하드웨어 불필요)."""

import sys
import types

import numpy as np
import pytest

from vocelab.audio.engine import AudioEngine


class FakeOutStream:
    def __init__(self, **kw):
        self.kw = kw
        self.started = False
        self.closed = False

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def close(self):
        self.closed = True


class FakeSD:
    """sounddevice 대역 — OutputStream 생성/정지를 기록한다."""

    class CallbackStop(Exception):
        pass

    def __init__(self):
        self.streams = []
        self.stop_calls = 0

    def OutputStream(self, **kw):  # noqa: N802
        s = FakeOutStream(**kw)
        self.streams.append(s)
        return s

    def stop(self):
        self.stop_calls += 1


@pytest.fixture
def fake_sd(monkeypatch):
    fake = FakeSD()
    module = types.ModuleType("sounddevice")
    module.OutputStream = fake.OutputStream
    module.stop = fake.stop
    module.CallbackStop = FakeSD.CallbackStop
    monkeypatch.setitem(sys.modules, "sounddevice", module)
    return fake


def test_play_starts_outputstream_with_loop(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((1000, 1), dtype="float32")
    eng.play(loop=True)
    assert len(fake_sd.streams) == 1
    assert fake_sd.streams[0].started
    assert fake_sd.streams[0].kw["channels"] == 1


def test_play_noop_on_empty_buffer(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((0, 1), dtype="float32")
    eng.play()
    assert fake_sd.streams == []


def test_stop_playback_closes_stream(fake_sd):
    eng = AudioEngine()
    eng.last_recording = np.zeros((500, 1), dtype="float32")
    eng.play()
    eng.stop_playback()
    assert fake_sd.streams[0].closed
    assert fake_sd.stop_calls >= 1


# ---- 재생 블록 채우기 로직 (순수, sounddevice 불필요) -----------------------
def test_fill_block_non_loop_stops_at_end():
    data = np.arange(10, dtype="float32").reshape(-1, 1)
    block, pos, filled, stop = AudioEngine._fill_block(data, start=6, frames=8, loop=False)
    assert filled == 4 and stop is True
    assert np.array_equal(block[:4, 0], [6, 7, 8, 9])
    assert np.all(block[4:, 0] == 0)  # 나머지는 0으로 패딩


def test_fill_block_loop_wraps():
    data = np.arange(5, dtype="float32").reshape(-1, 1)
    block, pos, filled, stop = AudioEngine._fill_block(data, start=3, frames=7, loop=True)
    assert filled == 7 and stop is False
    # 3,4 → 되감아 0,1,2,3,4
    assert np.array_equal(block[:, 0], [3, 4, 0, 1, 2, 3, 4])
    assert pos == 5  # 끝 인덱스(다음 호출에서 0으로 되감김)


def test_play_callback_feeds_recent_buffer(fake_sd):
    """재생 콜백이 최근 버퍼를 채워 재생 중에도 스펙트럼이 갱신되게 한다."""
    eng = AudioEngine()
    eng.last_recording = (0.5 * np.ones((2000, 1))).astype("float32")
    eng.play()
    cb = fake_sd.streams[0].kw["callback"]
    out = np.zeros((512, 1), dtype="float32")
    cb(out, 512, None, None)
    assert eng.recent_samples().size >= 512
    assert np.allclose(out, 0.5)
