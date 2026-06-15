"""세션 저장소 + Api 기록 연동 테스트 (임시 디렉터리, 하드웨어 불필요)."""

import numpy as np

from vocelab.sessions import SessionStore
from vocelab.webapp import Api


def _payload(cpps=8.0, dur=1.2):
    return {
        "duration": dur,
        "waveform": [0.1, 0.2, 0.3],
        "spectrogram": [[0.1, 0.2]],
        "metrics": [
            {"key": "cpps", "label": "CPPS", "value": cpps, "status": "good", "unit": "dB"},
            {"key": "hnr", "label": "HNR", "value": 22.0, "status": "good", "unit": "dB"},
        ],
    }


def test_save_and_list(tmp_path):
    store = SessionStore(tmp_path)
    audio = np.zeros((4410, 1), dtype="float32")
    rec = store.save(_payload(7.5), audio, 44100, label="warmup")
    assert rec["cpps"] == 7.5 and rec["cpps_status"] == "good"
    listed = store.list()
    assert len(listed) == 1 and listed[0]["id"] == rec["id"]
    assert listed[0]["label"] == "warmup"


def test_get_and_audio_roundtrip(tmp_path):
    store = SessionStore(tmp_path)
    audio = (0.5 * np.sin(np.linspace(0, 50, 8000))).astype("float32")
    rec = store.save(_payload(), audio, 44100)
    doc = store.get(rec["id"])
    assert doc is not None and doc["payload"]["duration"] == 1.2
    loaded = store.audio(rec["id"])
    assert loaded is not None
    data, sr = loaded
    assert sr == 44100 and len(data) == 8000


def test_list_sorted_newest_first(tmp_path):
    store = SessionStore(tmp_path)
    ids = [store.save(_payload(), None, 44100)["id"] for _ in range(3)]
    # id에 uuid 접미사가 있어도 시간 접두사 기준 정렬이 안정적이도록 확인
    listed = [r["id"] for r in store.list()]
    assert listed == sorted(ids, reverse=True)


def test_set_label_and_delete(tmp_path):
    store = SessionStore(tmp_path)
    rec = store.save(_payload(), None, 44100)
    assert store.set_label(rec["id"], "후") is True
    assert store.get(rec["id"])["record"]["label"] == "후"
    assert store.delete(rec["id"]) is True
    assert store.get(rec["id"]) is None
    assert store.list() == []


def test_delete_sanitizes_path(tmp_path):
    store = SessionStore(tmp_path)
    # 경로 조작 시도는 안전 처리되어 아무것도 지우지 않음
    assert store.delete("../../etc/passwd") is False


def test_api_autosaves_on_stop(tmp_path, monkeypatch):
    api = Api(store=SessionStore(tmp_path))
    # stop_recording이 엔진을 호출하지 않도록 더미 데이터로 대체
    dummy = (0.3 * np.sin(np.linspace(0, 40, 44100))).astype("float32").reshape(-1, 1)
    monkeypatch.setattr(api.engine, "stop_recording", lambda: dummy)
    payload = api.stop_recording()
    assert payload.get("session_id")
    sessions = api.list_sessions()
    assert len(sessions) == 1
    assert api.get_session(sessions[0]["id"]) is not None
