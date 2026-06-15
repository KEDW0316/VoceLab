"""녹음 파형을 표시하는 위젯 (pyqtgraph 기반)."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg

from vocelab.dsp import envelope_downsample


class WaveformWidget(pg.PlotWidget):
    """모노/멀티채널 오디오 버퍼의 파형을 그린다.

    긴 녹음은 픽셀 수준으로 다운샘플(min/max 엔벨로프)하여 가볍게 렌더링한다.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setBackground("#1e1e1e")
        self.setMenuEnabled(False)
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel("bottom", "시간", units="s")
        self.setYRange(-1.0, 1.0)
        self._curve = self.plot(pen=pg.mkPen("#4ec9b0", width=1))

    def set_waveform(self, data: np.ndarray, samplerate: int) -> None:
        """오디오 버퍼를 파형으로 표시한다."""
        if data is None or len(data) == 0:
            self._curve.setData([], [])
            return

        # 멀티채널이면 첫 채널만 표시(M1). 추후 채널 선택/믹스 다운 추가.
        mono = data[:, 0] if data.ndim == 2 else data

        x, y = envelope_downsample(mono, samplerate)
        self._curve.setData(x, y)
        self.setXRange(0, len(mono) / samplerate, padding=0)
