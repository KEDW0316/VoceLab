"""녹음·재생 엔진.

버튼을 누르면 선택한 오디오 인터페이스에서 녹음을 시작하고, 정지하면 버퍼를
반환한다. 방금 녹음한 것을 바로 재생할 수 있다. (요구사항 1·2)

Qt에 비의존(순수 파이썬)하게 설계해 테스트·재사용이 쉽도록 한다. 실시간 입력
레벨은 `current_level`로 폴링하고, 녹음 완료는 `last_recording`으로 가져간다.
sounddevice는 지연 import 하여, 미설치 환경에서도 모듈 로드/단위 테스트가 가능하다.
"""

from __future__ import annotations

import threading

import numpy as np


class AudioEngine:
    """오디오 인터페이스 기반 녹음/재생 엔진."""

    def __init__(self, samplerate: int = 44100, channels: int = 1) -> None:
        self.samplerate = samplerate
        self.channels = channels

        self._stream = None  # sd.InputStream (녹음 중일 때만)
        self._out_stream = None  # sd.OutputStream (재생 중일 때만)
        self._monitor_stream = None  # sd.InputStream (상시 모니터: 스펙트럼용)
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._level = 0.0

        # 실시간 스펙트럼용 최근 모노 샘플 링버퍼
        self._recent = np.zeros(0, dtype="float32")
        self._recent_max = 8192  # 저음 피치 안정화를 위해 ~186ms 보관

        self.last_recording: np.ndarray | None = None

    # ---- 상태 ---------------------------------------------------------------
    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    @property
    def current_level(self) -> float:
        """가장 최근 오디오 블록의 RMS(0.0~1.0). 레벨미터용."""
        return self._level

    def _push_recent(self, mono: np.ndarray) -> None:
        """최근 모노 샘플 링버퍼 갱신 (락 안에서 호출)."""
        self._recent = np.concatenate([self._recent, np.asarray(mono, dtype="float32")])
        if self._recent.size > self._recent_max:
            self._recent = self._recent[-self._recent_max :]

    def recent_samples(self) -> np.ndarray:
        """실시간 스펙트럼용 최근 모노 샘플 복사본."""
        with self._lock:
            return self._recent.copy()

    # ---- 상시 모니터 (녹음 안 할 때도 스펙트럼이 흐르도록) -------------------
    def start_monitor(self, device: int | None = None) -> None:
        """입력을 계속 듣고 최근 버퍼만 갱신하는 경량 모니터 스트림.

        녹음 중에는 녹음 스트림이 최근 버퍼를 채우므로 불필요(이미 흐름).
        """
        if self.is_recording or self._monitor_stream is not None:
            return
        import sounddevice as sd

        def callback(indata, frames, time_info, status):  # noqa: ANN001
            mono = indata[:, 0] if indata.ndim == 2 else indata
            with self._lock:
                self._push_recent(mono)
            self._level = float(np.sqrt(np.mean(np.square(indata))))

        self._monitor_stream = sd.InputStream(
            samplerate=self.samplerate, channels=1, device=device, callback=callback
        )
        self._monitor_stream.start()

    def stop_monitor(self) -> None:
        if self._monitor_stream is not None:
            try:
                self._monitor_stream.stop()
                self._monitor_stream.close()
            except Exception:  # noqa: BLE001
                pass
            self._monitor_stream = None

    # ---- 녹음 ---------------------------------------------------------------
    def start_recording(
        self, device: int | None = None, channels: int | None = None
    ) -> None:
        """선택한 입력 장치에서 녹음을 시작한다.

        device: 입력 장치 인덱스(None이면 시스템 기본 입력).
        """
        if self.is_recording:
            raise RuntimeError("이미 녹음 중입니다.")

        import sounddevice as sd

        self.stop_playback()  # 재생(특히 loop) 중이면 멈추고 녹음 시작
        self.stop_monitor()  # 모니터 입력이 장치를 점유 중이면 해제
        ch = channels or self.channels
        self._frames = []
        self._recent = np.zeros(0, dtype="float32")
        self._level = 0.0

        def callback(indata, frames, time_info, status):  # noqa: ANN001
            # PortAudio 오디오 스레드에서 호출됨. 락으로 버퍼만 안전하게 적재.
            if status:
                # 언더런/오버런 등은 무시하되 추후 로깅 가능
                pass
            mono = indata[:, 0] if indata.ndim == 2 else indata
            with self._lock:
                self._frames.append(indata.copy())
                self._push_recent(mono)
            self._level = float(np.sqrt(np.mean(np.square(indata))))

        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=ch,
            device=device,
            callback=callback,
        )
        self._stream.start()

    def stop_recording(self) -> np.ndarray:
        """녹음을 정지하고 (frames, channels) float32 배열을 반환한다."""
        if not self.is_recording:
            raise RuntimeError("녹음 중이 아닙니다.")

        stream = self._stream
        self._stream = None
        stream.stop()
        stream.close()
        self._level = 0.0

        with self._lock:
            data = (
                np.concatenate(self._frames, axis=0)
                if self._frames
                else np.zeros((0, self.channels), dtype="float32")
            )
            self._frames = []

        self.last_recording = data
        return data

    # ---- 재생 ---------------------------------------------------------------
    @staticmethod
    def _fill_block(
        data: np.ndarray, start: int, frames: int, loop: bool
    ) -> tuple[np.ndarray, int, int, bool]:
        """재생 콜백용 블록 채우기. (block, next_pos, filled, stop)를 반환.

        loop면 끝에서 처음으로 되감고, 아니면 데이터 소진 시 stop=True.
        """
        n = len(data)
        ch = data.shape[1]
        out = np.zeros((frames, ch), dtype="float32")
        i, filled = start, 0
        while filled < frames:
            if i >= n:
                if loop:
                    i = 0
                else:
                    break
            take = min(frames - filled, n - i)
            out[filled : filled + take] = data[i : i + take]
            i += take
            filled += take
        return out, i, filled, (filled < frames and not loop)

    def play(
        self,
        data: np.ndarray | None = None,
        device: int | None = None,
        loop: bool = False,
        start_frame: int = 0,
    ) -> None:
        """방금 녹음한(또는 주어진) 버퍼를 즉시 재생한다.

        start_frame부터 재생 시작(DAW식 시킹). data가 None이면 가장 최근 녹음.
        loop=True면 stop_playback() 전까지 반복(끝에서 처음으로 되감음).
        재생 블록은 실시간 스펙트럼용 최근 버퍼에도 흘려보낸다.
        """
        import sounddevice as sd

        buf = self.last_recording if data is None else data
        if buf is None or len(buf) == 0:
            return

        self.stop_playback()
        pcm = np.asarray(buf, dtype="float32")
        if pcm.ndim == 1:
            pcm = pcm.reshape(-1, 1)
        start = int(max(0, min(start_frame, len(pcm) - 1)))
        pos = {"i": start}

        def callback(outdata, frames, time_info, status):  # noqa: ANN001
            block, pos["i"], filled, stop = self._fill_block(pcm, pos["i"], frames, loop)
            outdata[:] = block
            with self._lock:
                self._push_recent(block[:filled, 0])
            if stop:
                raise sd.CallbackStop

        self._out_stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=pcm.shape[1],
            device=device,
            callback=callback,
            finished_callback=self._on_playback_finished,
        )
        self._out_stream.start()

    def _on_playback_finished(self) -> None:
        self._out_stream = None

    def stop_playback(self) -> None:
        import sounddevice as sd

        if self._out_stream is not None:
            try:
                self._out_stream.stop()
                self._out_stream.close()
            except Exception:  # noqa: BLE001
                pass
            self._out_stream = None
        sd.stop()

    # ---- 저장 ---------------------------------------------------------------
    def save(self, path: str, data: np.ndarray | None = None) -> None:
        """녹음을 WAV/FLAC 등으로 저장한다 (확장자로 포맷 결정)."""
        import soundfile as sf

        buf = self.last_recording if data is None else data
        if buf is None or len(buf) == 0:
            raise ValueError("저장할 녹음이 없습니다.")
        sf.write(path, buf, self.samplerate)
