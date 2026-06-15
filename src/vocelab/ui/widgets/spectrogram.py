"""스펙트로그램 표시 위젯 (pyqtgraph ImageItem 기반)."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg

from vocelab.dsp import spectrogram_db


class SpectrogramWidget(pg.PlotWidget):
    """오디오 버퍼의 로그 파워 스펙트로그램을 그린다."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setBackground("#1e1e1e")
        self.setMenuEnabled(False)
        self.setLabel("bottom", "시간", units="s")
        self.setLabel("left", "주파수", units="Hz")

        self._img = pg.ImageItem()
        self.addItem(self._img)
        # 'inferno' 계열 컬러맵 (시각적으로 또렷)
        cmap = pg.colormap.get("inferno") if hasattr(pg.colormap, "get") else None
        if cmap is not None:
            self._img.setLookupTable(cmap.getLookupTable())

    def set_audio(self, data: np.ndarray, samplerate: int) -> None:
        if data is None or len(data) == 0:
            self._img.clear()
            return
        mono = data[:, 0] if data.ndim == 2 else data
        times, freqs, db = spectrogram_db(mono, samplerate)

        # ImageItem은 (cols=time, rows=freq) 방향으로 전치해 넣는다
        self._img.setImage(db.T, autoLevels=False, levels=(db.min(), db.max()))
        # 데이터 좌표계에 맞춰 위치/스케일 지정
        t_span = times[-1] if times.size else 1.0
        f_span = freqs[-1] if freqs.size else 1.0
        self._img.setRect(pg.QtCore.QRectF(0, 0, t_span, f_span))
        self.setXRange(0, t_span, padding=0)
        self.setYRange(0, f_span, padding=0)
