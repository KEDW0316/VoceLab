# 배포(패키징) 안내

## 로컬에서 직접 빌드
```bash
cd frontend && npm ci && npm run build && cd ..
pip install -r requirements.txt pyinstaller
pyinstaller packaging/vocelab.spec
# 결과: dist/VoceLab.exe (Windows) / dist/VoceLab.app (macOS)
```

## 자동 빌드 + 배포 (GitHub Actions)
1. 태그를 푸시하면 `.github/workflows/release.yml`이 Windows/macOS 바이너리를 빌드해
   Release에 첨부합니다.
   ```bash
   git tag v0.1.0 && git push origin v0.1.0
   ```
2. `workflow_dispatch`로 수동 실행해 빌드만 점검할 수도 있습니다(Actions 탭).

## 랜딩 페이지 (GitHub Pages)
- `site/`가 랜딩 페이지입니다. Settings → Pages → **Source: GitHub Actions** 로 설정하면
  `.github/workflows/pages.yml`이 `site/`를 배포합니다.

## 꼭 바꿀 것
- `frontend/src/lib/config.ts`의 `KOFI_URL` → 본인 Ko-fi 주소
- `site/index.html`의 `ko-fi.com/YOURNAME` (2곳) → 본인 Ko-fi 주소
- 저장소 주소(`kedw0316/vocelab`)가 맞는지 확인

## 알려진 이슈(첫 빌드 시 손볼 수 있음)
- **PyInstaller + 과학 패키지**(parselmouth/scipy/sounddevice)는 첫 빌드에서 누락
  모듈/데이터로 실패할 수 있습니다. 그럴 땐 `vocelab.spec`의 `hiddenimports`/`collect_all`
  에 해당 패키지를 추가하세요. (CI 로그의 ModuleNotFoundError를 보고 보완)
- **코드 서명 미적용**: Windows SmartScreen / macOS Gatekeeper 경고가 납니다.
  - Windows: "추가 정보 → 실행", macOS: 우클릭 → 열기
  - 정식 서명은 유료(Apple Developer $99/년, Windows 코드서명 인증서).
- **pywebview 런타임**: Windows는 WebView2(보통 기본 설치), macOS는 WKWebView 사용.
