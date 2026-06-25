"""PyInstaller 진입점 — VoceLab 웹앱(pywebview)을 실행한다."""

import sys

from vocelab.webapp import main

if __name__ == "__main__":
    sys.exit(main())
