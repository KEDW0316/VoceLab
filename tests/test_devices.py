"""오디오 장치 변환 로직 테스트 (실제 하드웨어 불필요)."""

from vocelab.audio.devices import _to_audio_devices


RAW_DEVICES = [
    {
        "name": "Scarlett 2i2",
        "max_input_channels": 2,
        "max_output_channels": 2,
        "default_samplerate": 48000,
        "hostapi": 0,
    },
    {
        "name": "Built-in Output",
        "max_input_channels": 0,
        "max_output_channels": 2,
        "default_samplerate": 44100,
        "hostapi": 0,
    },
]
RAW_HOSTAPIS = [{"name": "Core Audio"}]


def test_input_filter_excludes_output_only():
    devs = _to_audio_devices(RAW_DEVICES, RAW_HOSTAPIS, want="input")
    assert [d.name for d in devs] == ["Scarlett 2i2"]
    assert devs[0].index == 0
    assert devs[0].is_input
    assert devs[0].hostapi_name == "Core Audio"


def test_output_filter_includes_both():
    devs = _to_audio_devices(RAW_DEVICES, RAW_HOSTAPIS, want="output")
    assert [d.name for d in devs] == ["Scarlett 2i2", "Built-in Output"]


def test_label_includes_hostapi():
    devs = _to_audio_devices(RAW_DEVICES, RAW_HOSTAPIS, want="input")
    assert devs[0].label == "Scarlett 2i2 [Core Audio]"
