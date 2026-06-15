# VoceLab

보컬 트레이닝 보조 데스크톱 앱. 오디오 인터페이스로 마이크를 받아 녹음하고,
즉시 모니터링하며, Praat 수준의 음향 지표(CPP 등)로 발성을 분석한다.

> 설계 전반은 [`PLANNING.md`](./PLANNING.md) 참고.

## 현재 상태 — M1 (녹음/재생 코어)

- ✅ 오디오 인터페이스(입/출력) 열거·선택
- ✅ 버튼으로 녹음 시작/정지, 입력 레벨미터
- ✅ 녹음 즉시 재생 (방금 발성을 바로 모니터링)
- ✅ 녹음 파형 표시
- ⏳ CPP/CPPS 등 음향 분석 (M2~)

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
