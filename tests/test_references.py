"""출처 데이터 무결성 + 생성 문서 동기화 테스트."""

from pathlib import Path

from vocelab.analysis.metrics import _METRIC_SPEC
from vocelab.analysis.references import REFERENCES, reference_for

ROOT = Path(__file__).resolve().parent.parent


def test_every_metric_has_a_reference():
    for key, *_ in _METRIC_SPEC:
        assert reference_for(key) is not None, f"'{key}' 지표에 출처가 없음"


def test_references_have_valid_fields():
    for key, ref in REFERENCES.items():
        assert ref.title, f"{key}: title 비어있음"
        assert ref.citation, f"{key}: citation 비어있음"
        assert ref.url.startswith("http"), f"{key}: url 형식 이상 ({ref.url})"
        assert ref.summary, f"{key}: summary 비어있음"
        if ref.secondary_url:
            assert ref.secondary_url.startswith("http"), f"{key}: secondary_url 형식 이상"


def test_no_unknown_reference_keys():
    """REFERENCES의 모든 키는 실제 지표 키여야 한다(오타 방지)."""
    metric_keys = {key for key, *_ in _METRIC_SPEC}
    assert set(REFERENCES) <= metric_keys, set(REFERENCES) - metric_keys


def test_generated_doc_is_in_sync():
    """docs/REFERENCES.md가 references.py와 동기화되어 있어야 한다.

    드리프트 시: `PYTHONPATH=src python tools/gen_references.py` 로 재생성.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "gen_references", ROOT / "tools" / "gen_references.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    expected = mod.render()
    actual = (ROOT / "docs" / "REFERENCES.md").read_text(encoding="utf-8")
    assert actual == expected, "docs/REFERENCES.md 가 오래됨 — gen_references.py 재실행 필요"
