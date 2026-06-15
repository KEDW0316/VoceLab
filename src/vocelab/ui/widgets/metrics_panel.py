"""음향 지표 표시 패널 (카테고리별 그룹 + 스크롤)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from vocelab.analysis import VoiceMetrics


class MetricsPanel(QWidget):
    """VoiceMetrics를 카테고리별 카드로 보여주는 스크롤 패널.

    각 카드는 라벨/값+단위를 표시하고, 마우스를 올리면 설명·정상범위를 툴팁으로 보여준다.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        title = QLabel("음향 지표")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px;")
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, stretch=1)

        self._content = QWidget()
        self._box = QVBoxLayout(self._content)
        self._box.setAlignment(Qt.AlignTop)
        self._box.setSpacing(4)
        scroll.setWidget(self._content)

        self._placeholder = QLabel("녹음 후 분석 결과가 여기에 표시됩니다.")
        self._placeholder.setStyleSheet("color: #888; padding: 8px;")
        self._box.addWidget(self._placeholder)

        self._widgets: list[QWidget] = []
        self.setMinimumWidth(250)

    def set_metrics(self, metrics: VoiceMetrics) -> None:
        for w in self._widgets:
            w.setParent(None)
        self._widgets.clear()
        self._placeholder.hide()

        current_category: str | None = None
        for m in metrics.metrics:
            if m.category != current_category:
                current_category = m.category
                header = QLabel(current_category)
                header.setStyleSheet(
                    "color: #c586c0; font-size: 12px; font-weight: bold;"
                    "padding: 6px 2px 2px 2px;"
                )
                self._box.addWidget(header)
                self._widgets.append(header)

            card = self._make_card(m.label, m.display, m.unit, m.description, m.normal)
            self._box.addWidget(card)
            self._widgets.append(card)

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
        box.setContentsMargins(10, 5, 10, 5)
        box.setSpacing(1)

        name = QLabel(label)
        name.setStyleSheet("color: #9cdcfe; font-size: 12px;")

        val_row = QHBoxLayout()
        val = QLabel(value)
        val.setStyleSheet("color: #4ec9b0; font-size: 18px; font-weight: bold;")
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
