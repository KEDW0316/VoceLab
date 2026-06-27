# VoceLab — 보컬 트레이닝 보조 앱 설계서

보컬 트레이닝을 위한 데스크톱 앱. 오디오 인터페이스로 마이크를 받아 녹음하고,
즉시 모니터링하며, Praat 수준의 음향 지표(CPP 등)로 발성을 객관적으로 분석한다.

## 1. 요구사항

1. DAW처럼 오디오 인터페이스(오인페)로 마이크 입력을 받을 수 있어야 함
2. 버튼을 누르고 발성한 뒤, 방금 녹음한 것을 바로 들어볼 수 있어야 함
3. Praat처럼 CPP(Cepstral Peak Prominence) 지표를 보여줄 수 있어야 함
4. 그 외 논문/임상에서 효과가 검증된 음향 지표들을 보여줄 수 있어야 함

## 2. 기술 스택

| 영역 | 선택 | 근거 |
|---|---|---|
| 언어 | Python 3.11+ | 음향 분석 생태계가 가장 풍부 |
| 오디오 I/O | `sounddevice` (PortAudio) | 오디오 인터페이스 멀티채널, 저지연 녹음/재생. Win=ASIO/WASAPI, mac=CoreAudio |
| 음향 분석 | `parselmouth`(Praat) | CPP/지터/쉬머/HNR/포먼트를 Praat 엔진 그대로 산출 |
| 수치 처리 | `numpy`, `scipy` | 신호 처리 기반 |
| UI | `pywebview` + React/TypeScript | 네이티브 셸 안의 웹 UI. 파이썬 백엔드를 `window.pywebview.api`로 노출. 한/영 i18n |
| 패키징 | `PyInstaller` + Inno Setup / hdiutil | Windows `.exe` 설치 프로그램 · macOS `.dmg` |

> 초기 계획은 `PySide6` + `pyqtgraph` 데스크톱 UI였으나, 웹 기반 UI(React)가
> 레이아웃·모션·다국어에서 더 유연해 `pywebview` 셸로 전환했다. 오디오/분석
> 백엔드는 동일하게 Qt 비의존 순수 파이썬으로 유지된다.

### 왜 Parselmouth인가
요구사항 3(Praat처럼 CPP)이 스택을 결정한다. Parselmouth는 Praat 엔진을
파이썬에서 직접 호출하므로 CPP/CPPS·지터·쉬머·HNR·포먼트를 **Praat과 수치까지
동일하게** 산출한다. 직접 구현 대비 검증 부담이 없고 신뢰성이 보장된다.

### 왜 데스크톱(브라우저 아님)인가
Web Audio API는 전문 오디오 인터페이스 멀티채널 접근과 과학적 분석 정밀도에
제약이 크다. 네이티브 파이썬에서 PortAudio로 직접 받는 편이 지연·정확도 모두 유리.

## 3. 표시 지표 (논문 근거)

### 1차 — 음질 핵심
- **CPPS** (Cepstral Peak Prominence Smoothed): 가장 robust한 음질 지표. ASHA 권장,
  음성장애·기식성과 강한 상관. (Hillenbrand 1994; Maryn 2009)
- **HNR** (Harmonics-to-Noise Ratio): 잡음 대비 배음 에너지
- **Jitter / Shimmer**: 주기·진폭 섭동 (성대 안정성)

### 발성·호흡
- **H1–H2, 스펙트럼 기울기(spectral tilt)**: 기식성·성대 접촉도
- **Alpha ratio, Hammarberg index**: 발성 노력·음색 밝기 (Acoustic Voice Quality Index 구성요소)

### 노래 특화
- **Singer's Formant / SPR** (Singing Power Ratio, 2.8–3.4kHz 공명): 성악적 울림
- **Vibrato rate & extent**: 비브라토 주기/폭
- **F0 안정성·피치 정확도**

### 음역
- **VRP / Phonetogram** (Voice Range Profile): 음높이별 음압 프로파일
- **MPT** (Maximum Phonation Time): 최대 발성 지속시간

> 종합 지표인 **AVQI / ABI** (CPPS+다지표 가중합)를 후속으로 도입해
> 단일 점수로 추세를 보여주는 것도 고려.

## 4. 아키텍처

```
src/vocelab/
  audio/        # 오디오 인터페이스 I/O (sounddevice)
    devices.py    # 입출력 장치 열거/선택
    engine.py     # 녹음·재생 엔진 (프레임워크 비의존)
  analysis/     # 음향 분석 (parselmouth)
    metrics.py
  dsp.py        # 파형/스펙트럼 변환 (순수 numpy/scipy)
  scales.py     # 보컬 워밍업 스케일
  sessions.py   # 녹음 저장·기록
  webapp.py     # pywebview 진입점 + JS에 노출되는 Api 클래스
frontend/       # React + TypeScript + Vite 웹 UI (한/영 i18n)
  src/
    components/
    lib/          # api 브리지, i18n, content(번역 테이블)
```

웹 UI와 오디오/분석 엔진을 분리한다. 엔진은 UI 비의존(순수 파이썬)으로 두어
테스트·재사용이 쉽게 한다. UI는 `webapp.Api`를 통해서만 백엔드와 통신한다.

## 5. 로드맵

- ✅ **M1 — 녹음/재생 코어**: 오인페 선택 → 버튼 녹음 → 즉시 재생 + 파형/레벨미터. (요구 1·2)
- ✅ **M2 — CPP 분석**: Parselmouth로 CPPS 산출·표시. 스펙트로그램. (요구 3)
- ✅ **M3 — 지표 확장**: HNR·지터·쉬머·포먼트·Alpha/Hammarberg/SPR·비브라토. (요구 4)
- **M4 — 세션 기록**: 녹음 저장·전후 비교, VRP 누적.
- **M5 — 패키징/배포**: PyInstaller로 Win/mac 빌드.

## 6. 실행 방법

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m vocelab
```
