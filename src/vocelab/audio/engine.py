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
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._level = 0.0

        self.last_recording: np.ndarray | None = None

    # ---- 상태 ---------------------------------------------------------------
    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    @property
    def current_level(self) -> float:
        """가장 최근 오디오 블록의 RMS(0.0~1.0). 레벨미터용."""
        return self._level

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

        sd.stop()  # 재생(특히 loop) 중이면 멈추고 녹음 시작
        ch = channels or self.channels
        self._frames = []
        self._level = 0.0

        def callback(indata, frames, time_info, status):  # noqa: ANN001
            # PortAudio 오디오 스레드에서 호출됨. 락으로 버퍼만 안전하게 적재.
            if status:
                # 언더런/오버런 등은 무시하되 추후 로깅 가능
                pass
            with self._lock:
                self._frames.append(indata.copy())
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
    def play(
        self,
        data: np.ndarray | None = None,
        device: int | None = None,
        loop: bool = False,
    ) -> None:
        """방금 녹음한(또는 주어진) 버퍼를 즉시 재생한다.

        data가 None이면 가장 최근 녹음을 재생한다.
        loop=True면 stop_playback() 전까지 반복 재생한다(귀 훈련용).
        """
        import sounddevice as sd

        buf = self.last_recording if data is None else data
        if buf is None or len(buf) == 0:
            return
        sd.play(buf, samplerate=self.samplerate, device=device, loop=loop)

    def stop_playback(self) -> None:
        import sounddevice as sd

        sd.stop()

    # ---- 저장 ---------------------------------------------------------------
    def save(self, path: str, data: np.ndarray | None = None) -> None:
        """녹음을 WAV/FLAC 등으로 저장한다 (확장자로 포맷 결정)."""
        import soundfile as sf

        buf = self.last_recording if data is None else data
        if buf is None or len(buf) == 0:
            raise ValueError("저장할 녹음이 없습니다.")
        sf.write(path, buf, self.samplerate)
