# 음향 지표 출처 (References)

VoceLab가 표시하는 각 지표의 근거 논문과 요약. 앱의 각 지표 카드에 있는
**📄 출처** 링크가 아래 1차 출처로 연결된다.

> 인용·DOI/URL은 서브에이전트 웹 조사로 교차검증했다. 다만 다수 출판사·학술
> 사이트가 자동 페치를 차단해 일부 URL은 직접 렌더링 검증은 못 했고, 여러
> 검색 결과로 메타데이터를 교차 확인했다. 책·워크숍 문서 등 일부는 DOI가 없다.

## CPPS  (`cpps`)

**1차 출처** — Hillenbrand & Houde (1996)

> Hillenbrand, J., & Houde, R. A. (1996). Acoustic correlates of breathy vocal quality: Dysphonic voices and continuous speech. Journal of Speech and Hearing Research, 39(2), 311–321.

링크: <https://doi.org/10.1044/jshr.3902.311>

CPPS는 켑스트럼 피크의 두드러짐(= 신호의 주기성/배음 강도)을 정량화한다. 이 논문은 평활 CPP가 '기식성(breathiness)' 지각과 가장 강하게 상관하는 음향 지표임을 보였다. CPPS가 낮을수록 기식성·음성장애가 크다. 보편적 임상 컷오프는 이 논문이 제시하지 않으며 녹음·알고리즘에 따라 달라진다.

**보조 출처**: Maryn, Y., De Bodt, M., & Roy, N. (2010). The Acoustic Voice Quality Index (AVQI). Journal of Communication Disorders, 43(3), 161–174 — CPPS를 핵심 가중치로 쓰는 다지표 음성장애 종합지표.

링크: <https://doi.org/10.1016/j.jcomdis.2009.12.004>

---

## HNR  (`hnr`)

**1차 출처** — Boersma (1993)

> Boersma, P. (1993). Accurate short-term analysis of the fundamental frequency and the harmonics-to-noise ratio of a sampled sound. Proceedings of the Institute of Phonetic Sciences (Amsterdam), 17, 97–110.

링크: <https://www.fon.hum.uva.nl/paul/papers/Proceedings_1993.pdf>

Praat의 HNR 구현 근거 논문. 자기상관(lag-domain) 기반으로 신호를 주기 성분과 잡음 성분으로 나눠 HNR = 10·log10(주기/잡음)[dB]로 계산한다. HNR이 높을수록 주기적이고 잡음이 적은(덜 기식적인) 발성이다.

**보조 출처**: Yumoto, E., Gould, W. J., & Baer, T. (1982). Harmonics-to-noise ratio as an index of the degree of hoarseness. JASA, 71(6), 1544–1550.

링크: <https://doi.org/10.1121/1.387808>

---

## 평균 F0  (`f0_mean`)

**1차 출처** — Boersma (1993)

> Boersma, P. (1993). Accurate short-term analysis of the fundamental frequency and the harmonics-to-noise ratio of a sampled sound. Proceedings of the Institute of Phonetic Sciences (Amsterdam), 17, 97–110.

링크: <https://www.fon.hum.uva.nl/paul/papers/Proceedings_1993.pdf>

Praat의 기본주파수(피치) 추정 근거 논문. 자기상관 기반으로 잡음·지터가 있어도 F0를 정확히 추정한다. 평균 F0는 발성의 평균 음높이를 나타낸다.

---

## F0 표준편차  (`f0_sd`)

**1차 출처** — Boersma (1993)

> Boersma, P. (1993). Accurate short-term analysis of the fundamental frequency and the harmonics-to-noise ratio of a sampled sound. Proceedings of the Institute of Phonetic Sciences (Amsterdam), 17, 97–110.

링크: <https://www.fon.hum.uva.nl/paul/papers/Proceedings_1993.pdf>

F0 표준편차는 피치 컨투어의 흔들림을 나타낸다(자기상관 피치 추정 기반). 지속발성에서는 낮을수록 음높이가 안정적이다.

---

## Jitter (local)  (`jitter`)

**1차 출처** — Titze (1995), NCVS

> Titze, I. R. (1995). Workshop on Acoustic Voice Analysis: Summary Statement. National Center for Voice and Speech (NCVS).

링크: <https://ncvs.org/archive/freebooks/summary-statement.pdf>

Jitter(local)는 연속 주기 간 기본주기의 섭동을 평균 절대차의 백분율로 나타낸다. 이 NCVS 합의 문서는 섭동 측정의 표준 방법론을 정의하고, 섭동 지표는 준주기적(Type 1) 신호에서만 신뢰할 수 있음을 명시한다. 건강한 발성은 보통 < 1%.

**보조 출처**: Brockmann, M., et al. (2008). Voice loudness and gender effects on jitter and shimmer in healthy adults. JSLHR, 51(5), 1152–1160 — 건강 성인 정상치.

링크: <https://pubmed.ncbi.nlm.nih.gov/18664710/>

---

## Shimmer (local)  (`shimmer`)

**1차 출처** — Titze (1995), NCVS

> Titze, I. R. (1995). Workshop on Acoustic Voice Analysis: Summary Statement. National Center for Voice and Speech (NCVS).

링크: <https://ncvs.org/archive/freebooks/summary-statement.pdf>

Shimmer(local)는 연속 주기 간 진폭 섭동을 평균 절대차(% 또는 dB)로 나타낸다. 같은 NCVS 문서가 jitter와 함께 정의하며 신호 유형 분류 틀을 제시한다. 건강한 발성은 보통 < 3.8%.

**보조 출처**: Brockmann, M., et al. (2008). Voice loudness and gender effects on jitter and shimmer in healthy adults. JSLHR, 51(5), 1152–1160 — 건강 성인 정상치.

링크: <https://pubmed.ncbi.nlm.nih.gov/18664710/>

---

## F1  (`f1`)

**1차 출처** — Fant (1960); Peterson & Barney (1952)

> Fant, G. (1960). Acoustic Theory of Speech Production. The Hague: Mouton.

링크: <https://openlibrary.org/books/OL16335889M/Acoustic_theory_of_speech_production>

포먼트(F1·F2·F3)는 성도(vocal tract)의 공명 주파수로 모음·음색을 결정한다. Fant의 단행본은 음원-필터 이론을 정립한 기초 문헌으로, 성도를 음향관으로 모델링해 그 공명이 포먼트가 됨을 보였다. LPC/Burg 추정의 이론적 토대.

**보조 출처**: Peterson, G. E., & Barney, H. L. (1952). Control methods used in a study of the vowels. JASA, 24(2), 175–184 — 모음별 포먼트 정상치의 고전적 출처.

링크: <https://doi.org/10.1121/1.1906875>

---

## F2  (`f2`)

**1차 출처** — Fant (1960); Peterson & Barney (1952)

> Fant, G. (1960). Acoustic Theory of Speech Production. The Hague: Mouton.

링크: <https://openlibrary.org/books/OL16335889M/Acoustic_theory_of_speech_production>

포먼트(F1·F2·F3)는 성도(vocal tract)의 공명 주파수로 모음·음색을 결정한다. Fant의 단행본은 음원-필터 이론을 정립한 기초 문헌으로, 성도를 음향관으로 모델링해 그 공명이 포먼트가 됨을 보였다. LPC/Burg 추정의 이론적 토대.

**보조 출처**: Peterson, G. E., & Barney, H. L. (1952). Control methods used in a study of the vowels. JASA, 24(2), 175–184 — 모음별 포먼트 정상치의 고전적 출처.

링크: <https://doi.org/10.1121/1.1906875>

---

## F3  (`f3`)

**1차 출처** — Fant (1960); Peterson & Barney (1952)

> Fant, G. (1960). Acoustic Theory of Speech Production. The Hague: Mouton.

링크: <https://openlibrary.org/books/OL16335889M/Acoustic_theory_of_speech_production>

포먼트(F1·F2·F3)는 성도(vocal tract)의 공명 주파수로 모음·음색을 결정한다. Fant의 단행본은 음원-필터 이론을 정립한 기초 문헌으로, 성도를 음향관으로 모델링해 그 공명이 포먼트가 됨을 보였다. LPC/Burg 추정의 이론적 토대.

**보조 출처**: Peterson, G. E., & Barney, H. L. (1952). Control methods used in a study of the vowels. JASA, 24(2), 175–184 — 모음별 포먼트 정상치의 고전적 출처.

링크: <https://doi.org/10.1121/1.1906875>

---

## Alpha ratio  (`alpha`)

**1차 출처** — Eyben et al. (2016), GeMAPS

> Eyben, F., et al. (2016). The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing. IEEE Transactions on Affective Computing, 7(2), 190–202.

링크: <https://doi.org/10.1109/TAFFC.2015.2457417>

Alpha ratio는 장기평균스펙트럼(LTAS)의 스펙트럼 균형 지표로, GeMAPS 정의로는 1–5 kHz 대 50 Hz–1 kHz 에너지 비(dB)다. 값이 높을수록(덜 음수) 고역 에너지가 많아 더 '밝고' 에너지 있는 음색이며, 발성 노력/음량과 함께 증가한다. 역사적 기원은 Frøkjær-Jensen & Prytz (1976)의 LTAS 스펙트럼 균형 측정이나 안정적 DOI가 없어, 검증 가능한 GeMAPS를 정의 출처로 둔다.

**보조 출처**: Frøkjær-Jensen, B., & Prytz, S. (1976). Registration of voice quality. Brüel & Kjær Technical Review, No. 3 — alpha 측정의 역사적 기원(DOI 없음).

---

## Hammarberg  (`hammarberg`)

**1차 출처** — Hammarberg et al. (1980)

> Hammarberg, B., Fritzell, B., Gauffin, J., Sundberg, J., & Wedin, L. (1980). Perceptual and acoustic correlates of abnormal voice qualities. Acta Oto-Laryngologica, 90(1–6), 441–451.

링크: <https://pubmed.ncbi.nlm.nih.gov/7211336/>

장애 음성에 대한 지각 평가와 LTAS 음향 측정을 상관시킨 연구로, 여기서 'Hammarberg index'(LTAS의 0–2 kHz 최대 − 2–5 kHz 최대, dB)가 유도됐다. 값이 클수록 저역에 에너지가 몰려(기식성/저기능 발성 경향), 작을수록 고역 에너지가 상대적으로 풍부하다.

**보조 출처**: Eyben, F., et al. (2016). GeMAPS, IEEE TAFFC, 7(2), 190–202 — 자동 분석용 Hammarberg index 밴드 정의 표준화.

링크: <https://doi.org/10.1109/TAFFC.2015.2457417>

---

## SPR  (`spr`)

**1차 출처** — Sundberg (1974); Omori et al. (1996)

> Omori, K., Kacker, A., Carroll, L. M., Riley, W. D., & Blaugrund, S. M. (1996). Singing power ratio: quantitative evaluation of singing voice quality. Journal of Voice, 10(3), 228–235.

링크: <https://pubmed.ncbi.nlm.nih.gov/8865093/>

SPR(Singing Power Ratio)은 2–4 kHz의 최대 배음 피크 대 0–2 kHz 최대 피크의 비로 정의된다(Omori 1996). 가수가 비가수보다 SPR이 유의하게 높았고(이 정의에선 높을수록 고역 피크 강함), 지각된 '링(ring)' 음색과 상관했다. 이론적 토대는 Sundberg(1974)의 'singing formant'(약 2.8–3.4 kHz 공명 군집) 연구다. (앱 구현은 0–2 kHz − 2–4 kHz 차로 계산하므로, 본 앱에서는 값이 낮을수록 링이 강하다.)

**보조 출처**: Sundberg, J. (1974). Articulatory interpretation of the 'singing formant.' JASA, 55(4), 838–844 — singer's formant의 음향/조음 기전.

링크: <https://doi.org/10.1121/1.1914609>

---

## 비브라토 rate  (`vibrato_rate`)

**1차 출처** — Prame (1994)

> Prame, E. (1994). Measurements of the vibrato rate of ten singers. The Journal of the Acoustical Society of America, 96(4), 1979–1984.

링크: <https://doi.org/10.1121/1.410141>

프로 성악가 10명의 비브라토 rate(F0 진동 주파수)를 측정해, 평균 약 6.0 Hz, 지속음 끝으로 갈수록 약 15% 상승함을 보였다. 노래 비브라토 rate의 표준 정상치 출처.

**보조 출처**: Sundberg, J. (1987). The Science of the Singing Voice. NIU Press — 비브라토를 약 5–7 Hz의 준정현파 F0 변동으로 특성화.

링크: <https://archive.org/details/scienceofsinging0000sund>

---

## 비브라토 extent  (`vibrato_extent`)

**1차 출처** — Prame (1997)

> Prame, E. (1997). Vibrato extent and intonation in professional Western lyric singing. The Journal of the Acoustical Society of America, 102(1), 616–621.

링크: <https://doi.org/10.1121/1.419735>

프로 성악가의 비브라토 extent(F0 변조의 peak-to-peak 깊이)를 측정해, 개별 음의 평균이 약 ±71 cents(범위 ±34–±123 cents, 약 1.4 반음 peak-to-peak)임을 보였다. extent는 음 길이와 음의 상관을 보였다. 비브라토 extent의 표준 정상치 출처.

**보조 출처**: Sundberg, J. (1987). The Science of the Singing Voice — extent 약 ±0.5–1 반음(약 1–2 반음 peak-to-peak)으로 특성화.

링크: <https://archive.org/details/scienceofsinging0000sund>

---
