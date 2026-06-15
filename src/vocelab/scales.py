"""보컬 연습용 기본 스케일 라이브러리.

각 스케일은 토닉(시작음) 기준 반음 오프셋 패턴으로 정의한다. 앱은 이 패턴을
가이드 톤으로 합성(synth.synthesize)해 들려주고, 토닉을 반음씩 옮겨가며(트랜스포즈)
코치처럼 워밍업을 진행할 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scale:
    key: str
    name: str
    description: str
    syllable: str  # 권장 음절/발성
    pattern: tuple[int, ...]  # 토닉 기준 반음 오프셋 (0 = 토닉)
    note_dur: float = 0.4  # 음당 길이(초)
    gap: float = 0.04  # 음 사이 간격(초)
    glide: bool = False  # True면 연속 글라이드(사이렌)
    total_dur: float = 4.0  # glide일 때 전체 길이(초)


SCALES: tuple[Scale, ...] = (
    Scale(
        key="five_tone",
        name="5-tone 스케일",
        description="도레미파솔파미레도. 가장 기본적인 음정 워밍업. 반음씩 올려가며 반복.",
        syllable="마/아 (ma)",
        pattern=(0, 2, 4, 5, 7, 5, 4, 2, 0),
        note_dur=0.38,
    ),
    Scale(
        key="major_octave",
        name="메이저 스케일 (옥타브)",
        description="도레미파솔라시도—시라솔파미레도. 한 옥타브 전체를 오르내린다.",
        syllable="아 (ah)",
        pattern=(0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0),
        note_dur=0.32,
    ),
    Scale(
        key="major_triad",
        name="아르페지오 (3화음)",
        description="도미솔도솔미도. 화음 음정 감각과 음역 확장에 좋다.",
        syllable="마/모 (mo)",
        pattern=(0, 4, 7, 12, 7, 4, 0),
        note_dur=0.4,
    ),
    Scale(
        key="staccato_arp",
        name="스타카토 아르페지오",
        description="도미솔미도를 짧게 끊어서. 성대 민첩성·온셋 훈련.",
        syllable="하/헤 (he)",
        pattern=(0, 4, 7, 4, 0),
        note_dur=0.16,
        gap=0.12,
    ),
    Scale(
        key="octave_jump",
        name="옥타브 점프",
        description="도—높은도—도. 넓은 음정 도약 연습.",
        syllable="우 (oo)",
        pattern=(0, 12, 0),
        note_dur=0.6,
    ),
    Scale(
        key="perfect_fifth",
        name="5도 (도-솔-도)",
        description="도솔도. 안정적인 음정과 지지(support) 감각.",
        syllable="아 (ah)",
        pattern=(0, 7, 0),
        note_dur=0.6,
    ),
    Scale(
        key="chromatic5",
        name="크로매틱 (반음)",
        description="반음씩 다섯 음 오르내린다. 정밀한 음정 컨트롤.",
        syllable="니/네 (ne)",
        pattern=(0, 1, 2, 3, 4, 3, 2, 1, 0),
        note_dur=0.32,
    ),
    Scale(
        key="lip_trill",
        name="립 트릴 (5-tone)",
        description="5-tone 패턴을 입술 트릴(브르르)로. SOVT 반폐쇄 성도 워밍업.",
        syllable="립 트릴 (brr)",
        pattern=(0, 2, 4, 5, 7, 5, 4, 2, 0),
        note_dur=0.38,
    ),
    Scale(
        key="sustained_vowel",
        name="지속 모음 (롱톤)",
        description="한 음을 길게 유지. CPP·지터·쉬머·HNR 측정에 최적. 호흡 지지력 훈련.",
        syllable="아 (ah)",
        pattern=(0,),
        note_dur=4.0,
        gap=0.0,
    ),
    Scale(
        key="siren",
        name="사이렌 (글라이드)",
        description="음을 끊지 않고 한 옥타브 오르내리며 미끄러뜨린다. 음역 전체를 부드럽게 연결.",
        syllable="응 (ng)",
        pattern=(0, 12, 0),
        glide=True,
        total_dur=4.0,
    ),
)

SCALES_BY_KEY: dict[str, Scale] = {s.key: s for s in SCALES}


def get_scale(key: str) -> Scale | None:
    return SCALES_BY_KEY.get(key)
