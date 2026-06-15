"""오디오 인터페이스(입출력 장치) 열거 및 선택.

sounddevice(PortAudio)를 통해 시스템에 연결된 오디오 인터페이스를 조회한다.
Qt에 비의존하도록 순수 데이터 구조(`AudioDevice`)만 반환한다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioDevice:
    """오디오 장치 한 개의 메타데이터."""

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    hostapi_name: str = ""

    @property
    def is_input(self) -> bool:
        return self.max_input_channels > 0

    @property
    def is_output(self) -> bool:
        return self.max_output_channels > 0

    @property
    def label(self) -> str:
        """UI 콤보박스에 표시할 라벨."""
        api = f" [{self.hostapi_name}]" if self.hostapi_name else ""
        return f"{self.name}{api}"


def _query() -> tuple[list[dict], list[dict]]:
    """sounddevice에서 (devices, hostapis)를 조회. import는 지연 로딩."""
    import sounddevice as sd  # 지연 import: 미설치 환경에서 모듈 로드 자체는 가능

    devices = list(sd.query_devices())
    hostapis = list(sd.query_hostapis())
    return devices, hostapis


def _to_audio_devices(
    devices: list[dict], hostapis: list[dict], *, want: str
) -> list[AudioDevice]:
    """raw 장치 dict 목록을 입력/출력 기준으로 필터링해 AudioDevice로 변환.

    `want`은 "input" 또는 "output".
    """
    result: list[AudioDevice] = []
    for idx, dev in enumerate(devices):
        chans = dev.get(
            "max_input_channels" if want == "input" else "max_output_channels", 0
        )
        if chans <= 0:
            continue
        api_idx = dev.get("hostapi", -1)
        api_name = hostapis[api_idx]["name"] if 0 <= api_idx < len(hostapis) else ""
        result.append(
            AudioDevice(
                index=idx,
                name=dev.get("name", f"device {idx}"),
                max_input_channels=dev.get("max_input_channels", 0),
                max_output_channels=dev.get("max_output_channels", 0),
                default_samplerate=float(dev.get("default_samplerate", 44100)),
                hostapi_name=api_name,
            )
        )
    return result


def input_devices() -> list[AudioDevice]:
    """녹음 가능한 입력 장치(오디오 인터페이스, 마이크) 목록."""
    devices, hostapis = _query()
    return _to_audio_devices(devices, hostapis, want="input")


def output_devices() -> list[AudioDevice]:
    """재생 가능한 출력 장치 목록."""
    devices, hostapis = _query()
    return _to_audio_devices(devices, hostapis, want="output")
