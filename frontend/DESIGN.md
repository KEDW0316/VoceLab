# VoceLab 프론트엔드 디자인 규칙 (DESIGN.md)

이 문서는 AI/사람이 UI를 만들거나 고칠 때 따르는 **디자인 계약**이다. 모든 컴포넌트는
여기 정의된 토큰과 규칙만 사용한다. ("generic AI 느낌"을 피하고 일관성을 유지하기 위함.)

## 무드 — Pro Audio / DAW 다크
오디오 인터페이스·DAW 느낌. 짙은 차콜 배경 위에 네온 틸 액센트, 계측기 같은
또렷한 숫자. 파형·스펙트로그램·레벨미터가 주인공.

## 색 (토큰만 사용 — 하드코딩 hex 금지)
CSS 변수는 `src/index.css`의 `:root`에 정의. Tailwind 토큰으로만 참조한다.

- `background` 짙은 차콜 / `card` 한 단계 밝은 패널 / `popover` 더 밝은 표면
- `foreground` 본문 / `muted-foreground` 보조 텍스트
- `primary` 네온 틸(액센트·강조·녹음 외 동작) / `accent` 바이올렛(카테고리·보조 강조)
- `border` 저대비 경계 / `ring` 포커스(=primary)
- 상태: `success`(틸그린) `warning`(앰버) `danger`(레드) — 레벨미터·경고·녹음
- 레벨미터: green→amber→red 그라데이션 (`--level-*`)

## 타이포
- 본문/라벨: 시스템 산세리프 (`font-sans`)
- **수치(지표 값·주파수·시간)**: `font-mono tabular-nums` — 계측기 느낌, 자리 안 흔들림
- 위계: 페이지 타이틀 18px / 섹션 13px 세미볼드 / 라벨 11–12px / 지표 값 20–24px 볼드

## 간격·모서리
- 간격 스케일: 4·8·12·16·24px (Tailwind 1·2·3·4·6)
- 모서리: 카드 `rounded-lg`, 작은 요소 `rounded-md` (DAW답게 과하지 않게)
- 카드: `bg-card border border-border`, 호버 시 `border-primary/40` 정도의 미묘한 강조만

## 컴포넌트 규칙
- 버튼/카드/셀렉트/배지는 `src/components/ui/*` 프리미티브만 사용. 새 스타일 인라인 금지.
- 아이콘은 `lucide-react`. 크기 14–18px, 색은 `text-muted-foreground` 기본.
- 모든 인터랙티브 요소에 포커스 링(`focus-visible:ring-ring`).
- **빈 상태(empty state)**: 데이터 없을 때 빈 박스 대신 안내 문구/아이콘을 보여준다.
- 숫자는 항상 단위와 함께, 단위는 작게 `text-muted-foreground`.

## UX 규칙
- 녹음 버튼은 가장 크고 눈에 띄게. 녹음 중엔 빨강 + 펄스 + 경과 시간 표시.
- 위험·되돌리기 어려운 동작만 빨강(`danger`). 일반 동작은 primary/secondary.
- 상태바는 항상 현재 무엇을 하는지 한 줄로 알려준다.
- 레벨미터는 green/amber/red 존으로 입력 과다(클리핑)를 시각적으로 경고.
- 키보드: 스페이스바로 녹음 토글(입력 포커스 아닐 때).

## 작업 루프 (셀프 리뷰)
1. 변경 → `npm run build`
2. QtWebEngine 오프스크린으로 스크린샷 캡처
3. 이 규칙에 비춰 스스로 비평 → 수정. 통과할 때까지 반복.
