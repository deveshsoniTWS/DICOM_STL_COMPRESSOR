"""
shared/pixels.py
Single frame pixel compression/decompression.

Lossless: tries JPEG2000 lossless and zstd level 22, picks smaller
Lossy:    JPEG2000 at aggressive rate
"""

import io

import numpy as np
import zstandard as zstd
from PIL import Image

_CCTX = zstd.ZstdCompressor(level=22)
_DCTX = zstd.ZstdDecompressor()


def compress_frame(frame: np.ndarray, mode: str) -> tuple[str, bytes]:
    """
    Compress a single 2D frame.

    Returns:
        (codec, compressed_bytes) — codec is 'j2k' or 'zstd'
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
    if mode == "lossless":
        return _decompress_lossless(codec, data, shape, dtype)
    return _decompress_lossy(data)


# ─── LOSSLESS ─────────────────────────────────────────────────────────────────


def _compress_lossless(frame: np.ndarray) -> tuple[str, bytes]:
    # Option A: JPEG2000 lossless
    buf = io.BytesIO()
    if frame.dtype == np.uint8:
        img = Image.fromarray(frame, mode="L")
    else:
        img = Image.fromarray(frame.astype(np.uint16), mode="I;16")
    img.save(buf, format="jpeg2000", lossless=True)
    j2k_data = buf.getvalue()

    # Option B: zstd level 22
    zstd_data = _CCTX.compress(frame.tobytes())

    if len(j2k_data) <= len(zstd_data):
        return ("j2k", j2k_data)
    return ("zstd", zstd_data)


def _decompress_lossless(
    codec: str,
    data: bytes,
    shape: tuple,
    dtype: str,
) -> np.ndarray:
    if codec == "j2k":
        buf = io.BytesIO(data)
        img = Image.open(buf)
        return np.array(img, dtype=dtype)
    raw = _DCTX.decompress(data)
    return np.frombuffer(raw, dtype=dtype).reshape(shape).copy()


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
