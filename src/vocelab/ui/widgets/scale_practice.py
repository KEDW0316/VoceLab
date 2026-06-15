"""스케일 연습 위젯 — 스케일 선택, 토닉 트랜스포즈, 가이드 톤 재생."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from vocelab.scales import SCALES, Scale
from vocelab.synth import note_name_to_freq, solfege, synthesize

# 트랜스포즈용 토닉 후보 (C3~C5 반음 단위)
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_TONICS = [f"{n}{o}" for o in (3, 4, 5) for n in _NOTE_NAMES if not (o == 5 and n != "C")]


class ScalePracticeWidget(QGroupBox):
    """스케일을 골라 가이드 톤을 재생하고, 토닉을 반음씩 옮긴다.

    on_play_tone(buf): 가이드 톤 버퍼를 재생하도록 main_window가 주입.
    """

    def __init__(self, on_play_tone: Callable[[np.ndarray], None], parent=None) -> None:
        super().__init__("스케일 연습", parent)
        self._on_play_tone = on_play_tone
        self.samplerate = 44100
        self._build_ui()
        self._on_scale_changed(0)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        row = QHBoxLayout()
        self.scale_combo = QComboBox()
        for s in SCALES:
            self.scale_combo.addItem(s.name, s.key)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_changed)
        row.addWidget(self.scale_combo, stretch=1)

        row.addWidget(QLabel("키:"))
        self.tonic_combo = QComboBox()
        self.tonic_combo.addItems(_TONICS)
        self.tonic_combo.setCurrentText("C4")
        self.tonic_combo.currentIndexChanged.connect(self._update_solfege)
        row.addWidget(self.tonic_combo)

        self.down_btn = QPushButton("▼반음")
        self.down_btn.clicked.connect(lambda: self._transpose(-1))
        row.addWidget(self.down_btn)
        self.up_btn = QPushButton("반음▲")
        self.up_btn.clicked.connect(lambda: self._transpose(+1))
        row.addWidget(self.up_btn)

        self.play_btn = QPushButton("▶ 가이드 톤")
        self.play_btn.clicked.connect(self._play)
        row.addWidget(self.play_btn)
        root.addLayout(row)

        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("color: #bbb;")
        root.addWidget(self.desc)

        self.solfege_label = QLabel()
        self.solfege_label.setStyleSheet("color: #4ec9b0; font-size: 13px;")
        root.addWidget(self.solfege_label)

    @property
    def current_scale(self) -> Scale:
        return SCALES[self.scale_combo.currentIndex()]

    def _on_scale_changed(self, _idx: int) -> None:
        s = self.current_scale
        self.desc.setText(f"{s.description}\n권장 음절: {s.syllable}")
        self._update_solfege()

    def _update_solfege(self) -> None:
        s = self.current_scale
        if s.glide:
            self.solfege_label.setText(f"키 {self.tonic_combo.currentText()} · 글라이드 ↗↘")
        else:
            self.solfege_label.setText(
                f"키 {self.tonic_combo.currentText()} · {solfege(s.pattern)}"
            )

    def _transpose(self, semitones: int) -> None:
        idx = self.tonic_combo.currentIndex() + semitones
        if 0 <= idx < self.tonic_combo.count():
            self.tonic_combo.setCurrentIndex(idx)  # _update_solfege 자동 호출

    def _play(self) -> None:
        tonic_hz = note_name_to_freq(self.tonic_combo.currentText())
        buf = synthesize(self.current_scale, tonic_hz, self.samplerate)
        self._on_play_tone(buf)
