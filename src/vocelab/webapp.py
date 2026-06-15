"""pywebview 백엔드 — 웹 프론트엔드(frontend/dist)에 Python API를 노출한다.

프론트엔드는 `window.pywebview.api.<method>()`로 아래 Api 메서드를 호출한다.
기존 모듈(audio/analysis/scales/synth/references)을 그대로 재사용하고, 결과를
JSON 직렬화 가능한 dict/list로 변환해 돌려준다.

페이로드 변환 함수는 모듈 함수로 분리해 하드웨어 없이 단위 테스트할 수 있게 한다.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vocelab.analysis import analyze
from vocelab.analysis.metrics import VoiceMetrics, to_mono_f64
from vocelab.analysis.rating import rate
from vocelab.analysis.references import reference_for
from vocelab.audio import AudioEngine, input_devices, output_devices
from vocelab.dsp import spectrogram_db
from vocelab.scales import SCALES, get_scale
from vocelab.synth import note_name_to_freq, solfege, synthesize

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


def spectrogram_payload(
    samples: np.ndarray, samplerate: int, freq_rows: int = 96, time_cols: int = 200
) -> list[list[float]]:
    """로그 스펙트로그램을 [freq][time] (0..1) 격자로 다운샘플."""
    mono = to_mono_f64(samples)
    if mono.size < 64:
        return []
    _times, freqs, db = spectrogram_db(mono, samplerate)  # db: (nf, nt) in [-90,0]
    norm = np.clip((db + 90.0) / 90.0, 0.0, 1.0)
    nf, nt = norm.shape
    fi = np.linspace(0, nf - 1, min(freq_rows, nf)).astype(int)
    ti = np.linspace(0, nt - 1, min(time_cols, nt)).astype(int)
    grid = norm[np.ix_(fi, ti)]
    return [[round(float(v), 3) for v in row] for row in grid]


def analysis_payload(samples: np.ndarray, samplerate: int) -> dict:
    return {
        "duration": round(len(samples) / samplerate, 3) if len(samples) else 0.0,
        "waveform": waveform_payload(samples),
        "spectrogram": spectrogram_payload(samples, samplerate),
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
    def __init__(self) -> None:
        self.engine = AudioEngine()
        self._output_index: int | None = None

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
        data = self.engine.stop_recording()
        return analysis_payload(data, self.engine.samplerate)

    def get_level(self) -> float:
        return float(self.engine.current_level)

    # 재생
    def play(self, loop: bool = False) -> None:
        self.engine.play(device=self._output_index, loop=bool(loop))

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
    """빌드된 프론트엔드 진입점 경로 (repo_root/frontend/dist/index.html)."""
    return Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"


def main() -> int:
    import webview

    index = _dist_index()
    if not index.exists():
        print(
            "프론트엔드 빌드가 없습니다. 먼저 빌드하세요:\n"
            "  cd frontend && npm install && npm run build"
        )
        return 1

    api = Api()
    webview.create_window(
        "VoceLab", url=index.as_uri(), js_api=api, width=1280, height=900, min_size=(1000, 720)
    )
    webview.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
