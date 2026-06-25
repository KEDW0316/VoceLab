# VoceLab

보컬 트레이닝 보조 **데스크톱 앱**. 오디오 인터페이스로 녹음하고 즉시 들어보며,
**실시간 음정·스펙트럼**과 **Praat 기반 음향 지표(CPPS·HNR·지터·쉬머)** 로 발성을
객관적으로 분석한다. 녹음·기록은 전부 로컬에만 저장된다(서버 전송 없음).

> 🌐 소개·다운로드: **https://kedw0316.github.io/VoceLab/**
> ☕ 후원: **https://ko-fi.com/pongtuna**

## 주요 기능
- 🎙 **녹음 & 즉시 재생** — 파형 클릭으로 원하는 지점부터 재생
- 🎵 **실시간 음정** — 노트+옥타브(한글 "2옥 도")와 센트, 녹음/재생/모니터 공통
- 📊 **실시간 스펙트럼** — DAW EQ식 막대 분석기 + 프리즈
- 🔬 **음향 지표** — CPPS·HNR·지터·쉬머(Praat 엔진), 양호/주의/개선 색 표시
- 🎹 **스케일 연습** — 워밍업 스케일 17종 + 가이드 톤 + 키 트랜스포즈
- 📈 **기록 & 전후 비교** — 녹음마다 자동 저장, 워밍업 전/후 델타

## 아키텍처
- **백엔드(Python)**: 오디오 I/O(`sounddevice`/PortAudio), 음향 분석(`praat-parselmouth`),
  신호처리(`scipy`/`numpy`). UI에 비의존이라 단독 테스트 가능.
- **프론트엔드(웹)**: React + TypeScript + Tailwind. `pywebview`가 네이티브 창에 띄우고,
  `window.pywebview.api`로 백엔드를 호출.

```
src/vocelab/        # Python: audio / analysis / dsp / scales / synth / sessions / webapp
frontend/           # React 웹 UI (Vite)
packaging/          # PyInstaller(.spec) + Inno Setup(.iss) 설치파일
site/               # 랜딩 페이지(GitHub Pages)
docs/               # 음향 지표 출처·발성 연습 레퍼런스
```

## 개발 환경에서 실행
사전: Python 3.11+, Node 18+

```bash
# 1) 프론트엔드 빌드 (UI 변경 시마다)
cd frontend && npm install && npm run build && cd ..

# 2) 백엔드 설치 후 실행
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e .
python -m vocelab
```
프론트엔드 단독 개발: `cd frontend && npm run dev` (백엔드 없으면 목 데이터로 동작).
디버그(개발자도구): `VOCELAB_DEBUG=1 python -m vocelab`.

## 테스트
```bash
pip install pytest
PYTHONPATH=src pytest        # 하드웨어 불필요한 단위 테스트
```

## 배포 (설치파일)
태그를 푸시하면 GitHub Actions가 Windows 설치 마법사(`VoceLab-Setup.exe`)와
macOS 디스크이미지(`VoceLab.dmg`)를 빌드해 Release에 첨부한다.
```bash
git tag v0.1.0 && git push origin v0.1.0
```
자세한 내용·서명 안내: [`packaging/README.md`](./packaging/README.md)

## 참고
- 의료·진단 도구가 아닙니다. 음성 문제가 지속되면 전문가(이비인후과/언어재활사) 상담을 권합니다.
- 지표 근거: [`docs/REFERENCES.md`](./docs/REFERENCES.md) · 발성 연습: [`docs/VOCAL_EXERCISES.md`](./docs/VOCAL_EXERCISES.md)

## 라이선스
[MIT](./LICENSE)
