"""세션(녹음 take) 영속 저장소.

녹음마다 오디오(WAV)와 분석 페이로드(JSON)를 디스크에 저장해, 과거 take를 다시
듣고 불러오고 전/후 비교할 수 있게 한다. 보컬 훈련의 핵심 = 시간에 따른 개선 추적.

WAV 입출력은 scipy.io.wavfile을 쓴다(soundfile 의존 회피). 저장 디렉터리는 기본
~/.vocelab/sessions 이며, 테스트는 임시 디렉터리를 주입한다.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np


def default_root() -> Path:
    return Path.home() / ".vocelab" / "sessions"


class SessionStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else default_root()
        self.root.mkdir(parents=True, exist_ok=True)

    # ---- 저장 ---------------------------------------------------------------
    def save(
        self,
        payload: dict,
        audio: np.ndarray | None,
        samplerate: int,
        label: str = "",
    ) -> dict:
        """분석 페이로드 + 오디오를 한 세션으로 저장하고 요약 레코드를 반환."""
        created = datetime.now()
        sid = created.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]

        if audio is not None and len(audio):
            from scipy.io import wavfile

            mono = audio[:, 0] if getattr(audio, "ndim", 1) == 2 else audio
            wavfile.write(self.root / f"{sid}.wav", samplerate, np.asarray(mono, dtype="float32"))

        record = {
            "id": sid,
            "created_at": created.isoformat(timespec="seconds"),
            "label": label,
            "samplerate": samplerate,
            "duration": payload.get("duration", 0.0),
        }
        doc = {"record": record, "payload": payload}
        (self.root / f"{sid}.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8"
        )
        return self._summary(doc)

    # ---- 조회 ---------------------------------------------------------------
    def list(self) -> list[dict]:
        """세션 요약 목록(최신순)."""
        out = []
        for f in self.root.glob("*.json"):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
                out.append(self._summary(doc))
            except (json.JSONDecodeError, KeyError, OSError):
                continue
        out.sort(key=lambda r: r["id"], reverse=True)
        return out

    def get(self, sid: str) -> dict | None:
        """전체 문서 {record, payload}. 없으면 None."""
        f = self.root / f"{self._safe(sid)}.json"
        if not f.exists():
            return None
        return json.loads(f.read_text(encoding="utf-8"))

    def audio(self, sid: str) -> tuple[np.ndarray, int] | None:
        """저장된 오디오를 (data, samplerate)로 로드. 없으면 None."""
        f = self.root / f"{self._safe(sid)}.wav"
        if not f.exists():
            return None
        from scipy.io import wavfile

        sr, data = wavfile.read(f)
        if data.dtype.kind == "i":  # 정수 PCM → float
            data = data.astype("float32") / np.iinfo(data.dtype).max
        return np.asarray(data, dtype="float32"), int(sr)

    def set_label(self, sid: str, label: str) -> bool:
        doc = self.get(sid)
        if doc is None:
            return False
        doc["record"]["label"] = label
        (self.root / f"{self._safe(sid)}.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8"
        )
        return True

    def delete(self, sid: str) -> bool:
        safe = self._safe(sid)
        removed = False
        for ext in (".json", ".wav"):
            p = self.root / f"{safe}{ext}"
            if p.exists():
                p.unlink()
                removed = True
        return removed

    # ---- 내부 ---------------------------------------------------------------
    @staticmethod
    def _safe(sid: str) -> str:
        # 경로 조작 방지: 파일명에 쓸 수 있는 문자만 허용
        return "".join(c for c in sid if c.isalnum() or c in "-_")

    @staticmethod
    def _summary(doc: dict) -> dict:
        rec = dict(doc["record"])
        metrics = doc.get("payload", {}).get("metrics", [])
        cpps = next((m for m in metrics if m["key"] == "cpps"), None)
        rec["cpps"] = cpps["value"] if cpps else None
        rec["cpps_status"] = cpps["status"] if cpps else "info"
        return rec
