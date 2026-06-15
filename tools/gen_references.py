"""`docs/REFERENCES.md`를 references.py 데이터로부터 생성한다.

references.py를 단일 출처로 유지하기 위해, 문서는 손으로 쓰지 않고 이 스크립트로
생성한다. 사용법:

    PYTHONPATH=src python tools/gen_references.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vocelab.analysis.metrics import _METRIC_SPEC  # noqa: E402
from vocelab.analysis.references import REFERENCES  # noqa: E402

# 지표 표시 라벨 (metrics 스펙에서 가져옴)
LABELS = {key: label for key, label, *_ in _METRIC_SPEC}


def render() -> str:
    lines = [
        "# 음향 지표 출처 (References)",
        "",
        "VoceLab가 표시하는 각 지표의 근거 논문과 요약. 앱의 각 지표 카드에 있는",
        "**📄 출처** 링크가 아래 1차 출처로 연결된다.",
        "",
        "> 인용·DOI/URL은 서브에이전트 웹 조사로 교차검증했다. 다만 다수 출판사·학술",
        "> 사이트가 자동 페치를 차단해 일부 URL은 직접 렌더링 검증은 못 했고, 여러",
        "> 검색 결과로 메타데이터를 교차 확인했다. 책·워크숍 문서 등 일부는 DOI가 없다.",
        "",
    ]

    # metrics 순서를 따른다
    for key, *_ in _METRIC_SPEC:
        ref = REFERENCES.get(key)
        if ref is None:
            continue
        label = LABELS.get(key, key)
        lines.append(f"## {label}  (`{key}`)")
        lines.append("")
        lines.append(f"**1차 출처** — {ref.title}")
        lines.append("")
        lines.append(f"> {ref.citation}")
        lines.append("")
        lines.append(f"링크: <{ref.url}>")
        lines.append("")
        lines.append(ref.summary)
        lines.append("")
        if ref.secondary:
            lines.append(f"**보조 출처**: {ref.secondary}")
            if ref.secondary_url:
                lines.append("")
                lines.append(f"링크: <{ref.secondary_url}>")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = ROOT / "docs" / "REFERENCES.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(render(), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(REFERENCES)} references)")


if __name__ == "__main__":
    main()
