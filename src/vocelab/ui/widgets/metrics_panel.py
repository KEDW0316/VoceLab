"""음향 지표 표시 패널."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from vocelab.analysis import VoiceMetrics


class MetricsPanel(QWidget):
    """VoiceMetrics를 카드 형태로 보여주는 패널.

    각 카드는 라벨/값+단위를 크게 표시하고, 마우스를 올리면 설명·정상범위를
    툴팁으로 보여준다.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignTop)

        title = QLabel("음향 지표")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px;")
        self._layout.addWidget(title)

        self._grid = QGridLayout()
        self._layout.addLayout(self._grid)

        self._placeholder = QLabel("녹음 후 분석 결과가 여기에 표시됩니다.")
        self._placeholder.setStyleSheet("color: #888; padding: 8px;")
        self._layout.addWidget(self._placeholder)

        self._cards: list[QWidget] = []
        self.setMinimumWidth(240)

    def set_metrics(self, metrics: VoiceMetrics) -> None:
        # 기존 카드 제거
        for card in self._cards:
            card.setParent(None)
        self._cards.clear()
        self._placeholder.hide()

        for row, m in enumerate(metrics.metrics):
            card = self._make_card(m.label, m.display, m.unit, m.description, m.normal)
            self._grid.addWidget(card, row, 0)
            self._cards.append(card)

    @staticmethod
    def _make_card(label, value, unit, desc, normal) -> QWidget:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background: #2a2d2e; border-radius: 6px; }"
            "QLabel { border: none; }"
        )
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        box = QVBoxLayout(frame)
        box.setContentsMargins(10, 6, 10, 6)
        box.setSpacing(1)

        name = QLabel(label)
        name.setStyleSheet("color: #9cdcfe; font-size: 12px;")

        val_row = QHBoxLayout()
        val = QLabel(value)
        val.setStyleSheet("color: #4ec9b0; font-size: 20px; font-weight: bold;")
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("color: #888; font-size: 11px;")
        val_row.addWidget(val)
        val_row.addWidget(unit_lbl)
        val_row.addStretch()

        box.addWidget(name)
        box.addLayout(val_row)

        tip = desc + (f"\n\n정상/참고: {normal}" if normal else "")
        frame.setToolTip(tip)
        return frame
