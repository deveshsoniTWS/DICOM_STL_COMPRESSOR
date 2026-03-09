"""
shared/parallel.py
Parallel frame compression for multi-frame DICOM.
"""

from concurrent.futures import ProcessPoolExecutor

import numpy as np

from shared.pixels import compress_frame, decompress_frame


def _compress_task(args: tuple) -> tuple[str, bytes]:
    frame, mode = args
    return compress_frame(frame, mode)


def compress_frames(pixel_array: np.ndarray, mode: str) -> list[tuple[str, bytes]]:
    n_frames = pixel_array.shape[0]
    tasks = [(pixel_array[i], mode) for i in range(n_frames)]
    workers = min(n_frames, 4)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(_compress_task, tasks))

    return results


def decompress_frames(
    chunks: list[tuple[str, bytes]],
    mode: str,
    frame_shape: tuple,
    dtype: str,
) -> np.ndarray:
    frames = [
        decompress_frame(codec, data, mode, frame_shape, dtype)
        for codec, data in chunks
    ]
    return np.stack(frames, axis=0)
