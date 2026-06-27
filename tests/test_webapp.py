"""webapp 페이로드 변환 + Api 테스트 (JSON 직렬화 가능 검증, 하드웨어 불필요)."""

import json

import numpy as np
import pytest

from vocelab.webapp import (
    Api,
    analysis_payload,
    metrics_payload,
    scale_payload,
    waveform_payload,
)
from vocelab.analysis import analyze
from vocelab.scales import get_scale

pytest.importorskip("parselmouth")

SR = 44100


def _vowel(dur=1.0, f0=220.0):
    t = np.arange(int(SR * dur)) / SR
    sig = np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)
    return sig.astype("float32")


def test_waveform_payload_downsamples_and_normalizes():
    wf = waveform_payload(_vowel(), points=600)
    assert len(wf) == 600
    assert all(0.0 <= v <= 1.0 for v in wf)


def test_waveform_payload_empty():
    assert waveform_payload(np.zeros((0, 1), dtype="float32")) == []


def test_metrics_payload_includes_reference_and_is_serializable():
    payload = metrics_payload(analyze(_vowel(), SR))
    assert len(payload) == 14
    cpps = next(m for m in payload if m["key"] == "cpps")
    assert cpps["reference"] is not None
    assert cpps["reference"]["url"].startswith("http")
    # 해석(rating) 필드 포함
    assert cpps["status"] in {"good", "watch", "poor", "info"}
    assert "note" in cpps
    # 전체가 JSON 직렬화 가능해야 함 (pywebview 브리지 요구사항)
    json.dumps(payload)


def test_analysis_payload_is_json_serializable():
    payload = analysis_payload(_vowel(1.2), SR)
    assert set(payload) == {"duration", "waveform", "metrics"}
    json.dumps(payload)  # numpy 타입이 남아있으면 여기서 실패


def test_scale_payload_solfege():
    p = scale_payload(get_scale("five_tone"), "C4")
    assert p["solfege"] == "도 레 미 파 솔 파 미 레 도"
    assert p["glide"] is False
    glide = scale_payload(get_scale("siren"), "C4")
    assert glide["glide"] is True


def test_api_list_scales_and_solfege():
    api = Api()
    scales = api.list_scales()
    assert len(scales) >= 8
    assert api.solfege_for("five_tone", "C4") == "도 레 미 파 솔 파 미 레 도"
    assert api.solfege_for("nope", "C4") == ""


def test_api_set_output_device():
    api = Api()
    api.set_output_device(3)
    assert api._output_index == 3
    api.set_output_device(None)
    assert api._output_index is None
