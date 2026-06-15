"""메인 윈도우 — 오인페 선택, 녹음/재생, 파형·스펙트로그램·음향지표. (M1+M2)"""

from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from vocelab.analysis import analyze
from vocelab.audio import AudioEngine, input_devices, output_devices
from vocelab.ui.widgets.metrics_panel import MetricsPanel
from vocelab.ui.widgets.spectrogram import SpectrogramWidget
from vocelab.ui.widgets.waveform import WaveformWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VoceLab")
        self.resize(1100, 680)

        self.engine = AudioEngine()
        self._input_index: int | None = None
        self._output_index: int | None = None

        self._build_ui()
        self._populate_devices()

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

        # 메인 영역: 좌(파형+스펙트로그램) / 우(음향지표)
        splitter = QSplitter(Qt.Horizontal)

        left = QWidget()
        left_box = QVBoxLayout(left)
        left_box.setContentsMargins(0, 0, 0, 0)
        self.waveform = WaveformWidget()
        self.spectrogram = SpectrogramWidget()
        left_box.addWidget(self.waveform, stretch=2)
        left_box.addWidget(self.spectrogram, stretch=3)
        splitter.addWidget(left)

        self.metrics_panel = MetricsPanel()
        splitter.addWidget(self.metrics_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, stretch=1)

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

        btn_row.addStretch()
        # 피드백 모드: 녹음이 끝나면 방금 부른 스케일을 자동(반복) 재생한다.
        self.feedback_check = QCheckBox("피드백 모드 (녹음 후 자동 반복재생)")
        self.feedback_check.setToolTip(
            "켜면 녹음을 멈추는 즉시 방금 녹음을 반복 재생합니다(귀 훈련용).\n"
            "끄면 일반 모드 — 녹음만 하고 지표가 표시됩니다(▶로 직접 재생)."
        )
        btn_row.addWidget(self.feedback_check)
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
            self.spectrogram.set_audio(data, self.engine.samplerate)
            has_audio = len(data) > 0
            self.play_btn.setEnabled(has_audio)
            secs = len(data) / self.engine.samplerate if has_audio else 0
            if has_audio:
                self.status.setText(f"녹음 완료 ({secs:.1f}s). 분석 중…")
                # UI를 먼저 갱신한 뒤 분석 실행
                QTimer.singleShot(0, lambda: self._run_analysis(data, secs))
                # 피드백 모드: 정지 즉시 방금 녹음을 반복 재생 (분석과 독립)
                if self.feedback_check.isChecked():
                    try:
                        self.engine.play(device=self._output_index, loop=True)
                    except Exception as exc:  # noqa: BLE001
                        self.status.setText(f"재생 실패: {exc}")
            else:
                self.status.setText("녹음된 오디오가 없습니다.")

    def _run_analysis(self, data, secs: float) -> None:
        try:
            metrics = analyze(data, self.engine.samplerate)
            self.metrics_panel.set_metrics(metrics)
            if self.feedback_check.isChecked():
                self.status.setText(
                    f"녹음 완료 ({secs:.1f}s). 🔁 반복 재생 중 — ■ 정지로 멈춤"
                )
            else:
                self.status.setText(
                    f"녹음 완료 ({secs:.1f}s). ▶ 재생으로 바로 들어보세요."
                )
        except Exception as exc:  # noqa: BLE001
            self.status.setText(f"분석 실패: {exc}")

    def _on_play(self) -> None:
        loop = self.feedback_check.isChecked()
        try:
            self.engine.play(device=self._output_index, loop=loop)
            self.status.setText("🔁 반복 재생 중 — ■ 정지로 멈춤" if loop else "재생 중…")
        except Exception as exc:  # noqa: BLE001
            self.status.setText(f"재생 실패: {exc}")

    def _update_level(self) -> None:
        rms = self.engine.current_level
        self.level_bar.setValue(int(min(1.0, rms * 4.0) * 100))

    def closeEvent(self, event) -> None:  # noqa: N802, ANN001
        if self.engine.is_recording:
            try:
                self.engine.stop_recording()
            except Exception:  # noqa: BLE001
                pass
        super().closeEvent(event)
