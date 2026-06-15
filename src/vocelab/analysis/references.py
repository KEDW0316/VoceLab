"""지표별 출처 논문·요약.

각 음향 지표가 어떤 논문에 근거하는지, 그 논문이 무엇을 밝혔는지를 담는다.
앱 UI는 지표 카드에 '📄 출처' 링크를 달아 브라우저로 논문을 열고, 별도의
`docs/REFERENCES.md` 문서는 이 데이터로부터 생성한다(단일 출처 유지).

서브에이전트 웹 조사로 인용·DOI/URL을 교차검증했다. 다만 출판사·학술 사이트가
자동 페치를 403으로 막아 일부 URL은 직접 렌더링 검증은 못 했고, 여러 검색 결과로
메타데이터(제목/저자/연도/DOI/PMID)를 교차 확인했다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Reference:
    title: str  # 짧은 표기 (예: "Hillenbrand & Houde (1996)")
    citation: str  # 전체 인용
    url: str  # 안정적 링크 (DOI/PubMed/아카이브)
    summary: str  # 이 논문이 밝힌 것 + 참고치
    secondary: str = ""  # 보조 인용 (선택)
    secondary_url: str = ""


_BOERSMA_1993 = (
    "Boersma, P. (1993). Accurate short-term analysis of the fundamental "
    "frequency and the harmonics-to-noise ratio of a sampled sound. "
    "Proceedings of the Institute of Phonetic Sciences (Amsterdam), 17, 97–110."
)
_BOERSMA_URL = "https://www.fon.hum.uva.nl/paul/papers/Proceedings_1993.pdf"

_TITZE_1995 = (
    "Titze, I. R. (1995). Workshop on Acoustic Voice Analysis: Summary "
    "Statement. National Center for Voice and Speech (NCVS)."
)
_TITZE_URL = "https://ncvs.org/archive/freebooks/summary-statement.pdf"

_BROCKMANN = (
    "Brockmann, M., et al. (2008). Voice loudness and gender effects on jitter "
    "and shimmer in healthy adults. JSLHR, 51(5), 1152–1160 — 건강 성인 정상치."
)
_BROCKMANN_URL = "https://pubmed.ncbi.nlm.nih.gov/18664710/"

_FORMANT = Reference(
    title="Fant (1960); Peterson & Barney (1952)",
    citation="Fant, G. (1960). Acoustic Theory of Speech Production. The Hague: Mouton.",
    url="https://openlibrary.org/books/OL16335889M/Acoustic_theory_of_speech_production",
    summary=(
        "포먼트(F1·F2·F3)는 성도(vocal tract)의 공명 주파수로 모음·음색을 결정한다. "
        "Fant의 단행본은 음원-필터 이론을 정립한 기초 문헌으로, 성도를 음향관으로 "
        "모델링해 그 공명이 포먼트가 됨을 보였다. LPC/Burg 추정의 이론적 토대."
    ),
    secondary=(
        "Peterson, G. E., & Barney, H. L. (1952). Control methods used in a study "
        "of the vowels. JASA, 24(2), 175–184 — 모음별 포먼트 정상치의 고전적 출처."
    ),
    secondary_url="https://doi.org/10.1121/1.1906875",
)


REFERENCES: dict[str, Reference] = {
    "cpps": Reference(
        title="Hillenbrand & Houde (1996)",
        citation=(
            "Hillenbrand, J., & Houde, R. A. (1996). Acoustic correlates of breathy "
            "vocal quality: Dysphonic voices and continuous speech. Journal of Speech "
            "and Hearing Research, 39(2), 311–321."
        ),
        url="https://doi.org/10.1044/jshr.3902.311",
        summary=(
            "CPPS는 켑스트럼 피크의 두드러짐(= 신호의 주기성/배음 강도)을 정량화한다. "
            "이 논문은 평활 CPP가 '기식성(breathiness)' 지각과 가장 강하게 상관하는 음향 "
            "지표임을 보였다. CPPS가 낮을수록 기식성·음성장애가 크다. 보편적 임상 컷오프는 "
            "이 논문이 제시하지 않으며 녹음·알고리즘에 따라 달라진다."
        ),
        secondary=(
            "Maryn, Y., De Bodt, M., & Roy, N. (2010). The Acoustic Voice Quality "
            "Index (AVQI). Journal of Communication Disorders, 43(3), 161–174 — "
            "CPPS를 핵심 가중치로 쓰는 다지표 음성장애 종합지표."
        ),
        secondary_url="https://doi.org/10.1016/j.jcomdis.2009.12.004",
    ),
    "hnr": Reference(
        title="Boersma (1993)",
        citation=_BOERSMA_1993,
        url=_BOERSMA_URL,
        summary=(
            "Praat의 HNR 구현 근거 논문. 자기상관(lag-domain) 기반으로 신호를 주기 성분과 "
            "잡음 성분으로 나눠 HNR = 10·log10(주기/잡음)[dB]로 계산한다. HNR이 높을수록 "
            "주기적이고 잡음이 적은(덜 기식적인) 발성이다."
        ),
        secondary=(
            "Yumoto, E., Gould, W. J., & Baer, T. (1982). Harmonics-to-noise ratio as "
            "an index of the degree of hoarseness. JASA, 71(6), 1544–1550."
        ),
        secondary_url="https://doi.org/10.1121/1.387808",
    ),
    "f0_mean": Reference(
        title="Boersma (1993)",
        citation=_BOERSMA_1993,
        url=_BOERSMA_URL,
        summary=(
            "Praat의 기본주파수(피치) 추정 근거 논문. 자기상관 기반으로 잡음·지터가 있어도 "
            "F0를 정확히 추정한다. 평균 F0는 발성의 평균 음높이를 나타낸다."
        ),
    ),
    "f0_sd": Reference(
        title="Boersma (1993)",
        citation=_BOERSMA_1993,
        url=_BOERSMA_URL,
        summary=(
            "F0 표준편차는 피치 컨투어의 흔들림을 나타낸다(자기상관 피치 추정 기반). "
            "지속발성에서는 낮을수록 음높이가 안정적이다."
        ),
    ),
    "jitter": Reference(
        title="Titze (1995), NCVS",
        citation=_TITZE_1995,
        url=_TITZE_URL,
        summary=(
            "Jitter(local)는 연속 주기 간 기본주기의 섭동을 평균 절대차의 백분율로 "
            "나타낸다. 이 NCVS 합의 문서는 섭동 측정의 표준 방법론을 정의하고, 섭동 지표는 "
            "준주기적(Type 1) 신호에서만 신뢰할 수 있음을 명시한다. 건강한 발성은 보통 < 1%."
        ),
        secondary=_BROCKMANN,
        secondary_url=_BROCKMANN_URL,
    ),
    "shimmer": Reference(
        title="Titze (1995), NCVS",
        citation=_TITZE_1995,
        url=_TITZE_URL,
        summary=(
            "Shimmer(local)는 연속 주기 간 진폭 섭동을 평균 절대차(% 또는 dB)로 나타낸다. "
            "같은 NCVS 문서가 jitter와 함께 정의하며 신호 유형 분류 틀을 제시한다. 건강한 "
            "발성은 보통 < 3.8%."
        ),
        secondary=_BROCKMANN,
        secondary_url=_BROCKMANN_URL,
    ),
    "f1": _FORMANT,
    "f2": _FORMANT,
    "f3": _FORMANT,
    "vibrato_rate": Reference(
        title="Prame (1994)",
        citation=(
            "Prame, E. (1994). Measurements of the vibrato rate of ten singers. The "
            "Journal of the Acoustical Society of America, 96(4), 1979–1984."
        ),
        url="https://doi.org/10.1121/1.410141",
        summary=(
            "프로 성악가 10명의 비브라토 rate(F0 진동 주파수)를 측정해, 평균 약 6.0 Hz, "
            "지속음 끝으로 갈수록 약 15% 상승함을 보였다. 노래 비브라토 rate의 표준 정상치 출처."
        ),
        secondary=(
            "Sundberg, J. (1987). The Science of the Singing Voice. NIU Press — "
            "비브라토를 약 5–7 Hz의 준정현파 F0 변동으로 특성화."
        ),
        secondary_url="https://archive.org/details/scienceofsinging0000sund",
    ),
    "vibrato_extent": Reference(
        title="Prame (1997)",
        citation=(
            "Prame, E. (1997). Vibrato extent and intonation in professional Western "
            "lyric singing. The Journal of the Acoustical Society of America, 102(1), 616–621."
        ),
        url="https://doi.org/10.1121/1.419735",
        summary=(
            "프로 성악가의 비브라토 extent(F0 변조의 peak-to-peak 깊이)를 측정해, 개별 음의 "
            "평균이 약 ±71 cents(범위 ±34–±123 cents, 약 1.4 반음 peak-to-peak)임을 보였다. "
            "extent는 음 길이와 음의 상관을 보였다. 비브라토 extent의 표준 정상치 출처."
        ),
        secondary=(
            "Sundberg, J. (1987). The Science of the Singing Voice — "
            "extent 약 ±0.5–1 반음(약 1–2 반음 peak-to-peak)으로 특성화."
        ),
        secondary_url="https://archive.org/details/scienceofsinging0000sund",
    ),
    "alpha": Reference(
        title="Eyben et al. (2016), GeMAPS",
        citation=(
            "Eyben, F., et al. (2016). The Geneva Minimalistic Acoustic Parameter "
            "Set (GeMAPS) for Voice Research and Affective Computing. IEEE "
            "Transactions on Affective Computing, 7(2), 190–202."
        ),
        url="https://doi.org/10.1109/TAFFC.2015.2457417",
        summary=(
            "Alpha ratio는 장기평균스펙트럼(LTAS)의 스펙트럼 균형 지표로, GeMAPS 정의로는 "
            "1–5 kHz 대 50 Hz–1 kHz 에너지 비(dB)다. 값이 높을수록(덜 음수) 고역 에너지가 "
            "많아 더 '밝고' 에너지 있는 음색이며, 발성 노력/음량과 함께 증가한다. 역사적 기원은 "
            "Frøkjær-Jensen & Prytz (1976)의 LTAS 스펙트럼 균형 측정이나 안정적 DOI가 없어, "
            "검증 가능한 GeMAPS를 정의 출처로 둔다."
        ),
        secondary=(
            "Frøkjær-Jensen, B., & Prytz, S. (1976). Registration of voice quality. "
            "Brüel & Kjær Technical Review, No. 3 — alpha 측정의 역사적 기원(DOI 없음)."
        ),
    ),
    "hammarberg": Reference(
        title="Hammarberg et al. (1980)",
        citation=(
            "Hammarberg, B., Fritzell, B., Gauffin, J., Sundberg, J., & Wedin, L. "
            "(1980). Perceptual and acoustic correlates of abnormal voice qualities. "
            "Acta Oto-Laryngologica, 90(1–6), 441–451."
        ),
        url="https://pubmed.ncbi.nlm.nih.gov/7211336/",
        summary=(
            "장애 음성에 대한 지각 평가와 LTAS 음향 측정을 상관시킨 연구로, 여기서 "
            "'Hammarberg index'(LTAS의 0–2 kHz 최대 − 2–5 kHz 최대, dB)가 유도됐다. 값이 "
            "클수록 저역에 에너지가 몰려(기식성/저기능 발성 경향), 작을수록 고역 에너지가 "
            "상대적으로 풍부하다."
        ),
        secondary=(
            "Eyben, F., et al. (2016). GeMAPS, IEEE TAFFC, 7(2), 190–202 — "
            "자동 분석용 Hammarberg index 밴드 정의 표준화."
        ),
        secondary_url="https://doi.org/10.1109/TAFFC.2015.2457417",
    ),
    "spr": Reference(
        title="Sundberg (1974); Omori et al. (1996)",
        citation=(
            "Omori, K., Kacker, A., Carroll, L. M., Riley, W. D., & Blaugrund, S. M. "
            "(1996). Singing power ratio: quantitative evaluation of singing voice "
            "quality. Journal of Voice, 10(3), 228–235."
        ),
        url="https://pubmed.ncbi.nlm.nih.gov/8865093/",
        summary=(
            "SPR(Singing Power Ratio)은 2–4 kHz의 최대 배음 피크 대 0–2 kHz 최대 피크의 비로 "
            "정의된다(Omori 1996). 가수가 비가수보다 SPR이 유의하게 높았고(이 정의에선 높을수록 "
            "고역 피크 강함), 지각된 '링(ring)' 음색과 상관했다. 이론적 토대는 Sundberg(1974)의 "
            "'singing formant'(약 2.8–3.4 kHz 공명 군집) 연구다. (앱 구현은 0–2 kHz − 2–4 kHz "
            "차로 계산하므로, 본 앱에서는 값이 낮을수록 링이 강하다.)"
        ),
        secondary=(
            "Sundberg, J. (1974). Articulatory interpretation of the 'singing "
            "formant.' JASA, 55(4), 838–844 — singer's formant의 음향/조음 기전."
        ),
        secondary_url="https://doi.org/10.1121/1.1914609",
    ),
}


def reference_for(key: str) -> Reference | None:
    return REFERENCES.get(key)
