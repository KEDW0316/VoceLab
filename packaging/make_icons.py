"""branding/VoceLab-1024.png 에서 .ico(Windows)·.icns(macOS) 아이콘을 생성한다.

CI(빌드) 단계에서 PyInstaller 전에 실행된다. 소스 PNG가 없으면 조용히 건너뛴다
(아이콘 없이도 빌드는 되도록).

사용: python packaging/make_icons.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SRC_CANDIDATES = [
    ROOT / "branding" / "VoceLab-1024.png",
    ROOT / "branding" / "icon.png",
    ROOT / "branding" / "VoceLab.png",
]


def main() -> int:
    src = next((p for p in SRC_CANDIDATES if p.exists()), None)
    if src is None:
        print("[make_icons] 소스 PNG 없음 → 아이콘 생성 건너뜀:", [str(p) for p in SRC_CANDIDATES])
        return 0

    from PIL import Image

    img = Image.open(src).convert("RGBA")

    ico_path = OUT / "icon.ico"
    img.save(ico_path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("[make_icons] wrote", ico_path)

    icns_path = OUT / "icon.icns"
    try:
        # .icns는 최소 사이즈 요건이 있어 1024 정사각으로 맞춰 저장
        square = img.resize((1024, 1024))
        square.save(icns_path)
        print("[make_icons] wrote", icns_path)
    except Exception as exc:  # noqa: BLE001
        print("[make_icons] icns 생성 실패(무시):", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
