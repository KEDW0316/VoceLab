"""지표 값을 good / watch / poor 로 해석한다.

원시 수치(예: "CPPS 8.9 dB")만으로는 사용자가 좋은지 알 수 없으므로, 문서화된
정상/참고 범위(references.py·임상 문헌)에 근거해 등급과 짧은 코멘트를 부여한다.

판단이 스타일·맥락 의존적이라 단정하기 어려운 지표(포먼트, alpha, SPR, F0 등)는
"info"(중립)로 두어 임의의 좋고 나쁨을 만들지 않는다 — 정직함을 위해.
"""

from __future__ import annotations

from dataclasses import dataclass

GOOD = "good"
WATCH = "watch"
POOR = "poor"
INFO = "info"  # 판단하지 않는 정보성 지표


@dataclass(frozen=True)
class Rule:
    better: str  # "high" | "low" | "band"
    good: float | None = None  # high/low: 임계값
    watch: float | None = None  # high/low: 경계 임계값
    band: tuple[float, float] | None = None  # band: good 구간
    watch_band: tuple[float, float] | None = None  # band: watch 구간
    notes: tuple[str, str, str] = ("", "", "")  # (good, watch, poor) 코멘트


# 등급 판정이 의미 있는 지표만 규칙을 둔다(나머지는 INFO).
_RULES: dict[str, Rule] = {
    "cpps": Rule(
        "high", good=4.0, watch=2.0,
        notes=("또렷하고 안정적인 발성", "약간 기식성이 있음", "기식성·거친 음질 가능"),
    ),
    "hnr": Rule(
        "high", good=20.0, watch=12.0,
        notes=("깨끗한 발성(잡음 적음)", "다소 잡음 섞임", "잡음/기식성 많음"),
    ),
    "jitter": Rule(
        "low", good=1.0, watch=2.0,
        notes=("음정(주기) 안정적", "약간 불안정", "주기 섭동 큼"),
    ),
    "shimmer": Rule(
        "low", good=3.8, watch=6.0,
        notes=("음량(진폭) 안정적", "약간 불안정", "진폭 섭동 큼"),
    ),
    "vibrato_rate": Rule(
        "band", band=(4.0, 7.0), watch_band=(3.0, 8.0),
        notes=("자연스러운 비브라토 주기", "주기가 다소 빠르거나 느림", "비브라토 주기가 범위 밖"),
    ),
    "vibrato_extent": Rule(
        "band", band=(0.5, 2.0), watch_band=(0.3, 3.0),
        notes=("적당한 비브라토 폭", "폭이 다소 좁거나 넓음", "비브라토 폭이 범위 밖"),
    ),
}


def rate(key: str, value: float | None) -> tuple[str, str]:
    """(status, note)를 반환. 규칙 없거나 값 없으면 ('info', '')."""
    rule = _RULES.get(key)
    if rule is None or value is None:
        return INFO, ""

    if rule.better == "high":
        status = GOOD if value >= rule.good else WATCH if value >= rule.watch else POOR
    elif rule.better == "low":
        status = GOOD if value <= rule.good else WATCH if value <= rule.watch else POOR
    else:  # band
        lo, hi = rule.band  # type: ignore[misc]
        wlo, whi = rule.watch_band  # type: ignore[misc]
        if lo <= value <= hi:
            status = GOOD
        elif wlo <= value <= whi:
            status = WATCH
        else:
            status = POOR

    note = rule.notes[{GOOD: 0, WATCH: 1, POOR: 2}[status]]
    return status, note


def direction(key: str) -> str | None:
    """전/후 비교 델타 색칠용 방향. 'high'(클수록 좋음)/'low'(작을수록 좋음)/None.

    밴드형(비브라토)·정보성 지표는 단순 방향이 없으므로 None.
    """
    rule = _RULES.get(key)
    if rule is None or rule.better == "band":
        return None
    return rule.better
