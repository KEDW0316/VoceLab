"""메인 윈도우 — 오디오 인터페이스 선택, 녹음/재생, 파형 표시. (M1)"""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from vocelab.audio import AudioEngine, input_devices, output_devices
from vocelab.ui.widgets.waveform import WaveformWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VoceLab")
        self.resize(900, 560)

        self.engine = AudioEngine()
        self._input_index: int | None = None
        self._output_index: int | None = None

        self._build_ui()
        self._populate_devices()

        # 녹음 중 입력 레벨을 주기적으로 폴링해 레벨미터 갱신
        self._level_timer = QTimer(self)
        self._level_timer.setInterval(50)
        self._level_timer.timeout.connect(self._update_level)

    # ---- UI 구성 ------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        # 장치 선택 줄
        dev_row = QHBoxLayout()
        dev_row.addWidget(QLabel("입력(오인페):"))
        self.input_combo = QComboBox()
        self.input_combo.currentIndexChanged.connect(self._on_input_changed)
        dev_row.addWidget(self.input_combo, stretch=1)

        dev_row.addWidget(QLabel("출력:"))
        self.output_combo = QComboBox()
        self.output_combo.currentIndexChanged.connect(self._on_output_changed)
        dev_row.addWidget(self.output_combo, stretch=1)

        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.clicked.connect(self._populate_devices)
        dev_row.addWidget(self.refresh_btn)
        root.addLayout(dev_row)

        # 파형
        self.waveform = WaveformWidget()
        root.addWidget(self.waveform, stretch=1)

        # 입력 레벨미터
        level_row = QHBoxLayout()
        level_row.addWidget(QLabel("입력 레벨:"))
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setTextVisible(False)
        level_row.addWidget(self.level_bar)
        root.addLayout(level_row)

        # 트랜스포트 버튼
        btn_row = QHBoxLayout()
        self.record_btn = QPushButton("● 녹음")
        self.record_btn.setCheckable(True)
        self.record_btn.toggled.connect(self._on_record_toggled)
        btn_row.addWidget(self.record_btn)

        self.play_btn = QPushButton("▶ 재생")
        self.play_btn.clicked.connect(self._on_play)
        self.play_btn.setEnabled(False)
        btn_row.addWidget(self.play_btn)

        self.stop_btn = QPushButton("■ 정지")
        self.stop_btn.clicked.connect(self.engine.stop_playback)
        btn_row.addWidget(self.stop_btn)
        root.addLayout(btn_row)

        self.status = QLabel("오디오 인터페이스를 선택하고 녹음을 시작하세요.")
        self.status.setAlignment(Qt.AlignCenter)
        root.addWidget(self.status)

        self.setCentralWidget(central)

    # ---- 장치 ---------------------------------------------------------------
    def _populate_devices(self) -> None:
        self.input_combo.blockSignals(True)
        self.output_combo.blockSignals(True)
        self.input_combo.clear()
        self.output_combo.clear()
        try:
            for dev in input_devices():
                self.input_combo.addItem(dev.label, dev.index)
            for dev in output_devices():
                self.output_combo.addItem(dev.label, dev.index)
        except Exception as exc:  # noqa: BLE001
            self.status.setText(f"오디오 장치 조회 실패: {exc}")
        finally:
            self.input_combo.blockSignals(False)
            self.output_combo.blockSignals(False)

        self._input_index = self.input_combo.currentData()
        self._output_index = self.output_combo.currentData()

    def _on_input_changed(self, _idx: int) -> None:
        self._input_index = self.input_combo.currentData()

    def _on_output_changed(self, _idx: int) -> None:
        self._output_index = self.output_combo.currentData()

    # ---- 녹음/재생 ----------------------------------------------------------
    def _on_record_toggled(self, checked: bool) -> None:
        if checked:
            try:
                self.engine.start_recording(device=self._input_index)
            except Exception as exc:  # noqa: BLE001
                self.record_btn.setChecked(False)
                self.status.setText(f"녹음 시작 실패: {exc}")
                return
            self.record_btn.setText("● 녹음 중… (정지)")
            self.play_btn.setEnabled(False)
            self.status.setText("녹음 중입니다. 발성하세요.")
            self._level_timer.start()
        else:
            self._level_timer.stop()
            self.level_bar.setValue(0)
            try:
                data = self.engine.stop_recording()
            except Exception as exc:  # noqa: BLE001
                self.status.setText(f"녹음 정지 실패: {exc}")
                return
            self.record_btn.setText("● 녹음")
            self.waveform.set_waveform(data, self.engine.samplerate)
            has_audio = len(data) > 0
            self.play_btn.setEnabled(has_audio)
            secs = len(data) / self.engine.samplerate if has_audio else 0
            self.status.setText(
                f"녹음 완료 ({secs:.1f}s). ▶ 재생으로 바로 들어보세요."
            )

    def _on_play(self) -> None:
        try:
            self.engine.play(device=self._output_index)
            self.status.setText("재생 중…")
        except Exception as exc:  # noqa: BLE001
            self.status.setText(f"재생 실패: {exc}")

    def _update_level(self) -> None:
        # RMS(0~1)를 dB 느낌으로 비선형 스케일해 미터 표시
        rms = self.engine.current_level
        self.level_bar.setValue(int(min(1.0, rms * 4.0) * 100))

    def closeEvent(self, event) -> None:  # noqa: N802, ANN001
        if self.engine.is_recording:
            try:
                self.engine.stop_recording()
            except Exception:  # noqa: BLE001
                pass
        super().closeEvent(event)
