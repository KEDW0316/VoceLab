"""가이드 톤 합성 (순수 numpy, Qt/하드웨어 비의존).

스케일 연습용 가이드 톤을 생성한다. 음표 시퀀스(토닉 기준 반음 오프셋)를 받아
부드러운 엔벨로프의 톤으로 합성하고, 사이렌류는 연속 글라이드로 합성한다.
"""

from __future__ import annotations

import numpy as np

A4_MIDI = 69
A4_HZ = 440.0

# 선택 가능한 토닉(시작음) — 보컬 음역을 충분히 커버
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# 이동도(movable-do) 솔페지 표시용 (토닉=도 기준, 반음계 포함)
_SOLFEGE = {
    0: "도", 1: "도#", 2: "레", 3: "미♭", 4: "미", 5: "파",
    6: "파#", 7: "솔", 8: "솔#", 9: "라", 10: "시♭", 11: "시",
}


def note_name_to_midi(name: str) -> int:
    """'C4', 'A#3' 같은 음이름을 MIDI 번호로 변환 (C4 = 60)."""
    name = name.strip().upper()
    # 끝의 정수(옥타브) 분리
    i = len(name)
    while i > 0 and (name[i - 1].isdigit() or name[i - 1] == "-"):
        i -= 1
    pitch, octave = name[:i], int(name[i:])
    if pitch not in _NOTE_NAMES:
        raise ValueError(f"알 수 없는 음이름: {name}")
    return (octave + 1) * 12 + _NOTE_NAMES.index(pitch)


def midi_to_freq(midi: float) -> float:
    return A4_HZ * 2.0 ** ((midi - A4_MIDI) / 12.0)


def note_name_to_freq(name: str) -> float:
    return midi_to_freq(note_name_to_midi(name))


def freq_to_note(hz: float) -> tuple[str, int, int]:
    """주파수(Hz)를 (음이름, 옥타브, 센트편차)로 변환. 예: 442 → ('A', 4, +8)."""
    midi = 69.0 + 12.0 * np.log2(hz / A4_HZ)
    nearest = int(round(midi))
    name = _NOTE_NAMES[nearest % 12]
    octave = nearest // 12 - 1
    cents = int(round((midi - nearest) * 100))
    return name, octave, cents


def solfege(pattern: tuple[int, ...]) -> str:
    """반음 오프셋 패턴을 이동도 솔페지 문자열로(표시용, 베스트에포트)."""
    out = []
    for semi in pattern:
        base = semi % 12
        octave_up = "˙" * (semi // 12)  # 옥타브 위 표시
        out.append(_SOLFEGE.get(base, _SOLFEGE.get(semi, f"+{semi}")) + octave_up)
    return " ".join(out)


def _tone(freq: float, dur: float, samplerate: int) -> np.ndarray:
    """배음 몇 개 + ADSR 엔벨로프를 가진 단음 (클릭 방지)."""
    n = max(1, int(samplerate * dur))
    t = np.arange(n) / samplerate
    wave = (
        np.sin(2 * np.pi * freq * t)
        + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
        + 0.15 * np.sin(2 * np.pi * 3 * freq * t)
    )
    wave *= _envelope(n, samplerate)
    return (0.3 * wave).astype(np.float32)


def _envelope(n: int, samplerate: int) -> np.ndarray:
    """짧은 어택/릴리즈 선형 램프 엔벨로프."""
    env = np.ones(n, dtype=np.float32)
    a = min(int(samplerate * 0.02), n // 2)  # 20ms 어택
    r = min(int(samplerate * 0.05), n // 2)  # 50ms 릴리즈
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.linspace(1, 0, r)
    return env


def _glide(pattern: tuple[int, ...], tonic_hz: float, total_dur: float, samplerate: int) -> np.ndarray:
    """패턴 지점들을 연속적으로 미끄러지는 글라이드(사이렌)."""
    freqs = np.array([tonic_hz * 2.0 ** (s / 12.0) for s in pattern], dtype=np.float64)
    n = max(2, int(samplerate * total_dur))
    # 패턴 지점을 시간축에 균등 배치 후 순간 주파수를 선형 보간
    xp = np.linspace(0, n, freqs.size)
    inst_freq = np.interp(np.arange(n), xp, freqs)
    phase = 2 * np.pi * np.cumsum(inst_freq) / samplerate
    wave = np.sin(phase) * _envelope(n, samplerate)
    return (0.3 * wave).astype(np.float32)


def synthesize(scale, tonic_hz: float, samplerate: int = 44100, tempo: float = 1.0) -> np.ndarray:
    """Scale을 토닉 주파수에서 가이드 톤 파형으로 합성한다.

    tempo > 1.0 이면 더 빠르게(음 길이 단축). 글라이드 스케일은 연속 합성한다.
    반환: (frames, 1) float32 (엔진 재생과 호환).
    """
    if scale.glide:
        mono = _glide(scale.pattern, tonic_hz, scale.total_dur / tempo, samplerate)
        return mono.reshape(-1, 1)

    note_dur = scale.note_dur / tempo
    gap = int(samplerate * scale.gap)
    silence = np.zeros(gap, dtype=np.float32)

    parts: list[np.ndarray] = []
    for semi in scale.pattern:
        freq = tonic_hz * 2.0 ** (semi / 12.0)
        parts.append(_tone(freq, note_dur, samplerate))
        if gap:
            parts.append(silence)
    mono = np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)
    return mono.reshape(-1, 1)
