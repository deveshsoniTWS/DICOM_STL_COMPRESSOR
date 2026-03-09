"""
shared/pixels.py
Single frame pixel compression/decompression.

Lossless: JPEG2000 lossless
Lossy:    JPEG2000 at aggressive rate
"""

import io

import numpy as np
from PIL import Image


def compress_frame(frame: np.ndarray, mode: str) -> tuple[str, bytes]:
    """
    Compress a single 2D frame.

    Returns:
        (codec, compressed_bytes) — codec is always 'j2k'
    """
    if mode == "lossless":
        return _compress_lossless(frame)
    return _compress_lossy(frame)


def decompress_frame(
    codec: str,
    data: bytes,
    mode: str,
    shape: tuple,
    dtype: str,
) -> np.ndarray:
    """
    Decompress a single frame.

    Args:
        codec: 'j2k' (only supported codec now)
        data:  compressed bytes
        mode:  'lossless' or 'lossy'
        shape: (H, W) — kept for API compatibility
        dtype: original numpy dtype string
    """
    if mode == "lossless":
        return _decompress_lossless(data, dtype)
    return _decompress_lossy(data)


# ─── LOSSLESS ─────────────────────────────────────────────────────────────────


def _compress_lossless(frame: np.ndarray) -> tuple[str, bytes]:
    buf = io.BytesIO()
    if frame.dtype == np.uint8:
        img = Image.fromarray(frame, mode="L")
    else:
        img = Image.fromarray(frame.astype(np.uint16), mode="I;16")
    img.save(buf, format="jpeg2000", lossless=True)
    return ("j2k", buf.getvalue())


def _decompress_lossless(data: bytes, dtype: str) -> np.ndarray:
    buf = io.BytesIO(data)
    img = Image.open(buf)
    return np.array(img, dtype=dtype)


# ─── LOSSY ────────────────────────────────────────────────────────────────────


def _compress_lossy(frame: np.ndarray) -> tuple[str, bytes]:
    buf = io.BytesIO()
    if frame.dtype == np.uint8:
        img = Image.fromarray(frame, mode="L")
    else:
        img = Image.fromarray(frame.astype(np.uint16), mode="I;16")
    img.save(buf, format="jpeg2000", quality_mode="rates", quality_layers=[20])
    return ("j2k", buf.getvalue())


def _decompress_lossy(data: bytes) -> np.ndarray:
    buf = io.BytesIO(data)
    img = Image.open(buf)
    return np.array(img)
