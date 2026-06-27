"""pywebview 백엔드 — 웹 프론트엔드(frontend/dist)에 Python API를 노출한다.

프론트엔드는 `window.pywebview.api.<method>()`로 아래 Api 메서드를 호출한다.
기존 모듈(audio/analysis/scales/synth/references)을 그대로 재사용하고, 결과를
JSON 직렬화 가능한 dict/list로 변환해 돌려준다.

페이로드 변환 함수는 모듈 함수로 분리해 하드웨어 없이 단위 테스트할 수 있게 한다.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

from vocelab.analysis import analyze
from vocelab.analysis.metrics import VoiceMetrics, to_mono_f64
from vocelab.analysis.rating import direction, rate
from vocelab.analysis.references import reference_for
from vocelab.audio import AudioEngine, input_devices, output_devices
from vocelab.dsp import representative_window, spectrum
from vocelab.scales import SCALES, get_scale
from vocelab.sessions import SessionStore
from vocelab.synth import freq_to_note, note_name_to_freq, solfege, synthesize

# ---- 페이로드 변환 (순수, 테스트 가능) -------------------------------------


def metrics_payload(metrics: VoiceMetrics) -> list[dict]:
    out = []
    for m in metrics.metrics:
        ref = reference_for(m.key)
        status, note = rate(m.key, m.value)
        out.append(
            {
                "key": m.key,
                "label": m.label,
                "value": None if m.value is None else float(m.value),
                "display": m.display,
                "unit": m.unit,
                "description": m.description,
                "normal": m.normal,
                "category": m.category,
                "status": status,
                "note": note,
                "better": direction(m.key),
                "reference": (
                    None
                    if ref is None
                    else {
                        "title": ref.title,
                        "citation": ref.citation,
                        "url": ref.url,
                        "summary": ref.summary,
                    }
                ),
            }
        )
    return out


def waveform_payload(samples: np.ndarray, points: int = 600) -> list[float]:
    """모노 진폭 엔벨로프(0..1)를 points개로 다운샘플."""
    mono = to_mono_f64(samples)
    if mono.size == 0:
        return []
    peak = float(np.max(np.abs(mono))) or 1.0
    if mono.size <= points:
        return [round(abs(float(v)) / peak, 4) for v in mono]
    bucket = mono.size // points
    usable = bucket * points
    env = np.abs(mono[:usable]).reshape(points, bucket).max(axis=1) / peak
    return [round(float(v), 4) for v in env]


def analysis_payload(samples: np.ndarray, samplerate: int) -> dict:
    # 스펙트로그램은 lean UI에서 제거됨 → 계산하지 않음(특히 긴 녹음에서 큰 비용 절감)
    return {
        "duration": round(len(samples) / samplerate, 3) if len(samples) else 0.0,
        "waveform": waveform_payload(samples),
        "metrics": metrics_payload(analyze(samples, samplerate)),
    }


def scale_payload(scale, tonic: str) -> dict:
    return {
        "key": scale.key,
        "name": scale.name,
        "description": scale.description,
        "syllable": scale.syllable,
        "glide": scale.glide,
        "solfege": "글라이드 ↗↘" if scale.glide else solfege(scale.pattern),
    }


def device_payload(dev) -> dict:
    return {"index": dev.index, "label": dev.label}


# ---- pywebview에 노출되는 API ----------------------------------------------


class Api:
    def __init__(self, store: SessionStore | None = None) -> None:
        self.engine = AudioEngine()
        self._output_index: int | None = None
        self.store = store or SessionStore()
        self._last_data: np.ndarray | None = None  # 분석 대기 중인 최근 녹음

    # 장치
    def list_devices(self) -> dict:
        try:
            return {
                "inputs": [device_payload(d) for d in input_devices()],
                "outputs": [device_payload(d) for d in output_devices()],
            }
        except Exception:  # noqa: BLE001
            return {"inputs": [], "outputs": []}

    def set_output_device(self, index) -> None:
        self._output_index = None if index is None else int(index)

    # 녹음/분석
    def start_recording(self, input_index) -> None:
        device = None if input_index is None else int(input_index)
        self.engine.start_recording(device=device)

    def stop_recording(self) -> dict:
        """녹음만 멈추고 즉시 가벼운 결과(길이·파형)를 반환한다.

        무거운 분석/저장은 analyze_current()에서 별도로 — 재생이 분석을 기다리지 않게.
        """
        data = self.engine.stop_recording()
        self._last_data = data
        return {
            "duration": round(len(data) / self.engine.samplerate, 3) if len(data) else 0.0,
            "waveform": waveform_payload(data),
            "metrics": [],
            "session_id": None,
        }

    def analyze_current(self) -> dict:
        """방금 녹음을 분석(지표)하고 세션에 저장한다. 재생 시작 후 백그라운드로 호출됨.

        지표는 전체가 아니라 '대표 구간'(에너지 강한 ~12초)에서만 계산한다
        — 긴 녹음 전체 지표는 의미가 옅고 느리므로. 파형·길이·저장 오디오는 전체.
        """
        data = self._last_data
        if data is None or len(data) == 0:
            return {"duration": 0.0, "waveform": [], "metrics": [], "session_id": None}
        sr = self.engine.samplerate
        seg = representative_window(to_mono_f64(data), sr)
        payload = {
            "duration": round(len(data) / sr, 3),
            "waveform": waveform_payload(data),
            "metrics": metrics_payload(analyze(seg, sr)),
        }
        try:
            rec = self.store.save(payload, data, sr)
            payload["session_id"] = rec["id"]
        except Exception:  # noqa: BLE001
            payload["session_id"] = None
        return payload

    # 세션(기록)
    def list_sessions(self) -> list[dict]:
        return self.store.list()

    def get_session(self, sid: str) -> dict | None:
        doc = self.store.get(sid)
        return doc["payload"] if doc else None

    def delete_session(self, sid: str) -> bool:
        return self.store.delete(sid)

    def label_session(self, sid: str, label: str) -> bool:
        return self.store.set_label(sid, label)

    def play_session(self, sid: str, loop: bool = False, start: float = 0.0) -> None:
        loaded = self.store.audio(sid)
        if loaded is None:
            return
        data, _sr = loaded
        self.engine.play(
            data=data,
            device=self._output_index,
            loop=bool(loop),
            start_frame=int(start * self.engine.samplerate),
        )

    def get_level(self) -> float:
        return float(self.engine.current_level)

    def get_spectrum(self) -> dict:
        """실시간 스펙트럼(EQ 곡선)용 최근 프레임 스펙트럼."""
        freqs, db = spectrum(self.engine.recent_samples(), self.engine.samplerate)
        return {"freqs": freqs, "db": db}

    def get_pitch(self) -> dict:
        """실시간 음정 — Praat(Parselmouth) 자기상관 피치로 F0 추정 후 노트/옥타브/센트.

        Praat 피치는 옥타브 점프 비용을 고려해 단순 자기상관보다 옥타브 에러에 강하다.
        최근 버퍼(녹음 입력/재생 오디오/마이크 모니터)를 그대로 분석하므로 셋 다 공통.
        """
        mono = to_mono_f64(self.engine.recent_samples())
        sr = self.engine.samplerate
        if mono.size < int(sr * 0.06):  # 60ms 미만이면 추정 불가
            return {"hz": None}
        try:
            import parselmouth

            snd = parselmouth.Sound(mono, sampling_frequency=sr)
            pitch = snd.to_pitch(0.01, 65.0, 1000.0)  # (time_step, floor, ceiling)
            freqs = pitch.selected_array["frequency"]
            voiced = freqs[freqs > 0]
            if voiced.size == 0:
                return {"hz": None}
            hz = float(np.median(voiced))
        except Exception:  # noqa: BLE001
            return {"hz": None}
        name, octave, cents = freq_to_note(hz)
        return {"hz": round(hz, 1), "note": name, "octave": octave, "cents": cents}

    def start_monitor(self, input_index=None) -> None:
        """상시 모니터 시작(녹음 안 할 때도 스펙트럼이 흐르도록)."""
        device = None if input_index is None else int(input_index)
        try:
            self.engine.start_monitor(device=device)
        except Exception:  # noqa: BLE001
            pass

    def stop_monitor(self) -> None:
        self.engine.stop_monitor()

    # 재생
    def play(self, loop: bool = False, start: float = 0.0) -> None:
        sr = self.engine.samplerate
        self.engine.play(
            device=self._output_index, loop=bool(loop), start_frame=int(start * sr)
        )

    def stop_playback(self) -> None:
        self.engine.stop_playback()

    # 스케일
    def list_scales(self) -> list[dict]:
        return [scale_payload(s, "C4") for s in SCALES]

    def solfege_for(self, scale_key: str, tonic: str) -> str:
        s = get_scale(scale_key)
        if s is None:
            return ""
        return "글라이드 ↗↘" if s.glide else solfege(s.pattern)

    def play_guide_tone(self, scale_key: str, tonic: str) -> None:
        s = get_scale(scale_key)
        if s is None:
            return
        buf = synthesize(s, note_name_to_freq(tonic), self.engine.samplerate)
        self.engine.play(data=buf, device=self._output_index, loop=False)


def _dist_index() -> Path:
    """빌드된 프론트엔드 진입점 경로.

    개발: repo_root/frontend/dist/index.html
    PyInstaller 패키지(frozen): 번들에 포함된 frontend/dist/index.html (sys._MEIPASS)
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / "frontend" / "dist" / "index.html"
    return Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"


def _runtime_dir() -> Path:
    """번들/소스 기준 리소스 디렉터리."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2] / "packaging"


def _window_icon() -> str | None:
    """Windows 작업표시줄/창 아이콘용 .ico 경로(있으면)."""
    if sys.platform != "win32":
        return None  # macOS는 .app 번들 아이콘이 처리
    ico = _runtime_dir() / "icon.ico"
    return str(ico) if ico.exists() else None


def main() -> int:
    import webview

    index = _dist_index()
    if not index.exists():
        print(
            "프론트엔드 빌드가 없습니다. 먼저 빌드하세요:\n"
            "  cd frontend && npm install && npm run build"
        )
        return 1

    # Windows: 작업표시줄이 python 호스트가 아닌 VoceLab으로 인식하도록 AppUserModelID 지정
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.vocelab.app")
        except Exception:  # noqa: BLE001
            pass

    api = Api()
    webview.create_window(
        "VoceLab", url=index.as_uri(), js_api=api, width=1280, height=900, min_size=(1000, 720)
    )
    # VOCELAB_DEBUG=1 로 실행하면 우클릭 → 검사(개발자도구)로 콘솔 확인 가능
    debug = os.environ.get("VOCELAB_DEBUG") in ("1", "true", "True")

    kwargs = {"debug": debug}
    icon = _window_icon()
    if icon:
        kwargs["icon"] = icon  # pywebview가 창/작업표시줄 아이콘으로 사용
    try:
        webview.start(**kwargs)
    except TypeError:
        # 설치된 pywebview가 icon 인자를 지원하지 않으면 무시하고 실행
        webview.start(debug=debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
