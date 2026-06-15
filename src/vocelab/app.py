"""애플리케이션 진입점."""

from __future__ import annotations

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from vocelab.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("VoceLab")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
