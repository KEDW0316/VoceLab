"""순수 신호 처리 헬퍼 (numpy만 의존, Qt/하드웨어 비의존).

UI·분석 양쪽에서 재사용하며 단위 테스트가 쉽도록 분리한다.
"""

from __future__ import annotations

import numpy as np


def envelope_downsample(
    mono: np.ndarray, samplerate: int, max_points: int = 4000
) -> tuple[np.ndarray, np.ndarray]:
    """min/max 엔벨로프로 파형을 다운샘플해 (x_seconds, y)를 반환한다.

    긴 녹음을 픽셀 수준으로 줄여 가볍게 렌더링하면서 피크 모양은 유지한다.
    """
    n = len(mono)
    if n <= max_points:
        x = np.arange(n) / samplerate
        return x, mono

    bucket = n // (max_points // 2)
    usable = (n // bucket) * bucket
    reshaped = mono[:usable].reshape(-1, bucket)
    mins = reshaped.min(axis=1)
    maxs = reshaped.max(axis=1)

    # min/max를 번갈아 배치해 엔벨로프 모양 유지
    y = np.empty(mins.size * 2, dtype=mono.dtype)
    y[0::2] = mins
    y[1::2] = maxs
    idx = np.repeat(np.arange(mins.size) * bucket, 2)
    x = idx / samplerate
    return x, y
