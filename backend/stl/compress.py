"""

stl/compress.py

STL compression — lossless and lossy modes.

Key techniques:

  - Drop normals entirely (both modes) — recomputed via cross product on decompress

  - Deduplicate with round(v, 6) — robust float dedup

  - Spatial sort → multiply by 1e6 → int64 → delta encode

  - Two streams: geometry (verts) + connectivity (faces)

"""

import gzip
import json
import os
import struct

import numpy as np
import zstandard as zstd

from shared.format import pack

_CCTX = zstd.ZstdCompressor(level=22)

PRECISION = 1_000_000


def compress(stl_path: str, mode: str) -> tuple[bytes, dict]:
    header, triangles = _parse_stl(stl_path)

    if mode == "lossless":
        meta_bytes, chunks = _compress_lossless(header, triangles)

    else:
        meta_bytes, chunks = _compress_lossy(header, triangles)

    compressed_bytes = pack(mode, "stl", meta_bytes, chunks)

    original_size = os.path.getsize(stl_path)

    compressed_size = len(compressed_bytes)

    ratio = round((1 - compressed_size / original_size) * 100, 2)

    stats = {
        "original_size_kb": round(original_size / 1024, 2),
        "compressed_size_kb": round(compressed_size / 1024, 2),
        "compression_ratio_pct": ratio,
        "mode": mode,
        "format": "STL",
        "n_triangles": len(triangles),
    }

    return compressed_bytes, stats


# ─── PARSE ────────────────────────────────────────────────────────────────────


def _parse_stl(path: str) -> tuple[bytes, np.ndarray]:
    """Vectorized binary STL parse — no Python loop."""

    with open(path, "rb") as f:
        header = f.read(80)

        n_tri = struct.unpack("<I", f.read(4))[0]

        dtype = np.dtype([("data", np.float32, (12,)), ("attr", np.uint16)])

        raw = np.frombuffer(f.read(n_tri * 50), dtype=dtype)

    return header, raw["data"]  # (N, 12)


# ─── DEDUP + DELTA ────────────────────────────────────────────────────────────


def _dedup_and_delta(verts_f32: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """

    1. Round to 6dp for robust deduplication

    2. np.unique → sorted unique verts + inverse (face indices)

    3. Multiply by 1e6 → int64 → delta encode

    Returns:

        deltas:  (U, 3) int64

        indices: (N, 3) int32

    """

    rounded = np.round(verts_f32, 6)

    unique_f, inverse = np.unique(rounded, axis=0, return_inverse=True)

    indices = inverse.reshape(-1, 3).astype(np.int32)

    int_verts = (unique_f * PRECISION).astype(np.int64)

    deltas = np.diff(int_verts, axis=0, prepend=int_verts[:1])

    return deltas, indices


# ─── LOSSLESS ─────────────────────────────────────────────────────────────────


def _compress_lossless(
    header: bytes,
    triangles: np.ndarray,
) -> tuple[bytes, list[tuple[str, bytes]]]:
    # Drop normals — recomputed on decompress via cross product

    all_verts = triangles[:, 3:].reshape(-1, 3)

    deltas, indices = _dedup_and_delta(all_verts)

    meta = json.dumps(
        {
            "_format": "stl",
            "_mode": "lossless",
            "_n_tri": int(triangles.shape[0]),
            "_n_unique": int(deltas.shape[0]),
            "_header_hex": header.hex(),
        }
    ).encode("utf-8")

    chunks = [
        ("zstd", _CCTX.compress(deltas.tobytes())),  # int64 delta verts
        ("zstd", _CCTX.compress(indices.tobytes())),  # face indices
    ]

    return gzip.compress(meta, compresslevel=9), chunks


# ─── LOSSY ────────────────────────────────────────────────────────────────────


def _compress_lossy(
    header: bytes,
    triangles: np.ndarray,
) -> tuple[bytes, list[tuple[str, bytes]]]:
    all_verts = triangles[:, 3:].reshape(-1, 3)

    # Quantize to uint16

    v_min = all_verts.min(axis=0)

    v_max = all_verts.max(axis=0)

    v_range = v_max - v_min

    v_range[v_range == 0] = 1

    quantized = ((all_verts - v_min) / v_range * 65535).astype(np.uint16)

    deltas, indices = _dedup_and_delta(quantized.astype(np.float32))

    meta = json.dumps(
        {
            "_format": "stl",
            "_mode": "lossy",
            "_n_tri": int(triangles.shape[0]),
            "_n_unique": int(deltas.shape[0]),
            "_header_hex": header.hex(),
            "_v_min": v_min.tolist(),
            "_v_max": v_max.tolist(),
        }
    ).encode("utf-8")

    chunks = [
        ("zstd", _CCTX.compress(deltas.tobytes())),
        ("zstd", _CCTX.compress(indices.tobytes())),
    ]

    return gzip.compress(meta, compresslevel=9), chunks
