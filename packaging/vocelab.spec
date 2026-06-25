# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 스펙 — repo 루트에서 `pyinstaller packaging/vocelab.spec` 로 빌드.
# 경로는 스펙 파일 위치(SPECPATH=packaging/) 기준이라, repo 루트를 따로 계산한다.
import os
import sys
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))  # repo 루트

# 아이콘(있으면 적용). make_icons.py가 생성.
_ico = os.path.join(SPECPATH, "icon.ico")
_icns = os.path.join(SPECPATH, "icon.icns")
exe_icon = _ico if (sys.platform == "win32" and os.path.exists(_ico)) else None
app_icon = _icns if os.path.exists(_icns) else None

datas = [(os.path.join(ROOT, "frontend", "dist"), "frontend/dist")]
binaries = []
hiddenimports = ["vocelab", "vocelab.webapp"]

for pkg in ["parselmouth", "scipy", "numpy", "sounddevice", "soundfile", "webview"]:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as exc:  # noqa: BLE001
        print(f"[spec] collect_all({pkg}) skipped: {exc}")

block_cipher = None

a = Analysis(
    [os.path.join(SPECPATH, "launcher.py")],
    pathex=[os.path.join(ROOT, "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["PySide6", "PyQt5", "PyQt6", "pyqtgraph", "matplotlib", "librosa", "numba", "tkinter", "IPython"],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VoceLab",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,  # GUI 앱(터미널 창 없음)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)

# macOS는 .app 번들로 감싼다.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="VoceLab.app",
        icon=app_icon,
        bundle_identifier="com.vocelab.app",
        info_plist={
            "NSMicrophoneUsageDescription": "VoceLab는 발성 녹음·분석을 위해 마이크를 사용합니다.",
            "NSHighResolutionCapable": True,
        },
    )
