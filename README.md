# VoceLab

보컬 트레이닝 보조 데스크톱 앱. 오디오 인터페이스로 마이크를 받아 녹음하고,
즉시 모니터링하며, Praat 수준의 음향 지표(CPP 등)로 발성을 분석한다.

> 설계 전반은 [`PLANNING.md`](./PLANNING.md) 참고.

## 현재 상태 — M3 (지표 확장)

- ✅ 오디오 인터페이스(입/출력) 열거·선택
- ✅ 버튼으로 녹음 시작/정지, 입력 레벨미터
- ✅ 녹음 즉시 재생 (방금 발성을 바로 모니터링)
- ✅ **피드백 모드** 토글: 켜면 녹음 정지 즉시 방금 스케일을 반복 재생(귀 훈련),
  끄면 일반 모드(녹음만·지표 표시). 두 모드 모두 지표는 그대로 산출
- ✅ 녹음 파형 + 스펙트로그램 표시
- ✅ CPPS·HNR·F0·지터·쉬머 (Praat 기반)
- ✅ 포먼트(F1–F3)·Alpha ratio·Hammarberg·SPR(Singer's Formant)·비브라토 rate/extent
- ✅ 카테고리별(음질/음높이/공명·음색/비브라토) 지표 패널
- ✅ 각 지표 카드의 **📄 출처** 링크 → 근거 논문(DOI/PubMed) 열기. 요약은 툴팁
- ⏳ 세션 저장·전후 비교, VRP (M4~)

### 지표 출처

각 지표의 근거 논문·요약은 [`docs/REFERENCES.md`](./docs/REFERENCES.md)에 정리되어 있고,
앱의 각 지표 카드 **📄 출처** 링크가 이 1차 출처로 연결된다. 출처 데이터의 단일 출처는
`src/vocelab/analysis/references.py`이며, 문서는 아래로 재생성한다(테스트가 동기화 검증):

```bash
PYTHONPATH=src python tools/gen_references.py
```

## 설치 & 실행

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m vocelab
```

> Windows에서 ASIO 저지연을 쓰려면 인터페이스 제조사 ASIO 드라이버를 설치하세요.
> macOS는 CoreAudio로 별도 드라이버 없이 동작합니다.

## 테스트

```bash
pip install pytest
pytest                              # 하드웨어 불필요한 단위 테스트
```

## 구조

```
src/vocelab/
  audio/      # sounddevice 기반 녹음/재생 (Qt 비의존)
  analysis/   # Parselmouth 기반 음향 분석 (M2+)
  ui/         # PySide6 UI
  app.py      # 진입점
```
