"""
stl/compress.py
STL compression — lossless and lossy modes.

Key technique: byte shuffle + delta + zstd
  Float32 bytes are interleaved: [b0,b1,b2,b3, b0,b1,b2,b3, ...]
  zstd can't see cross-float patterns. So we split into 4 byte planes:
  [b0,b0,...][b1,b1,...][b2,b2,...][b3,b3,...]
  Neighboring vertices have nearly identical high bytes → massive compression gain.
"""

import gzip
import json
import os
import struct

import numpy as np
import zstandard as zstd

from shared.format import pack

_CCTX = zstd.ZstdCompressor(level=22)


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
    """
    Parse binary STL — fully vectorized, no Python loop.
    Reads the whole body as a structured numpy array in one shot.
    """
    with open(path, "rb") as f:
        header = f.read(80)
        n_tri = struct.unpack("<I", f.read(4))[0]
        dtype = np.dtype(
            [
                ("data", np.float32, (12,)),
                ("attr", np.uint16),
            ]
        )
        raw = np.frombuffer(f.read(n_tri * 50), dtype=dtype)

    triangles = raw["data"]  # (N, 12)
    return header, triangles


# ─── BYTE SHUFFLE ─────────────────────────────────────────────────────────────


def _byte_shuffle(arr: np.ndarray) -> bytes:
    """
    Split float32 into 4 separate byte planes for better zstd compression.
    [b0,b1,b2,b3, b0,b1,b2,b3, ...] → [b0,b0,..., b1,b1,..., b2,b2,..., b3,b3,...]
    """
    raw = np.ascontiguousarray(arr, dtype=np.float32).tobytes()
    b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4)
    return b.T.copy().tobytes()


# ─── LOSSLESS ─────────────────────────────────────────────────────────────────


def _compress_lossless(
    header: bytes,
    triangles: np.ndarray,
) -> tuple[bytes, list[tuple[str, bytes]]]:
    normals = triangles[:, :3]  # (N, 3)
    all_verts = triangles[:, 3:].reshape(-1, 3)  # (N*3, 3)

    # Deduplicate vertices → index buffer
    unique_verts, inverse = np.unique(all_verts, axis=0, return_inverse=True)
    indices = inverse.reshape(-1, 3).astype(np.int32)  # (N, 3)

    # Delta encode — np.unique sorts, so consecutive verts are close
    delta_verts = np.diff(unique_verts, axis=0, prepend=unique_verts[:1])

    meta = json.dumps(
        {
            "_format": "stl",
            "_mode": "lossless",
            "_n_tri": int(triangles.shape[0]),
            "_n_unique": int(unique_verts.shape[0]),
            "_header_hex": header.hex(),
        }
    ).encode("utf-8")

    chunks = [
        # normals — byte shuffled
        ("zstd", _CCTX.compress(_byte_shuffle(normals))),
        # delta vertices — byte shuffled (biggest win here)
        ("zstd", _CCTX.compress(_byte_shuffle(delta_verts))),
        # indices — plain zstd (integers, no shuffle needed)
        ("zstd", _CCTX.compress(indices.tobytes())),
    ]

    return gzip.compress(meta, compresslevel=9), chunks


# ─── LOSSY ────────────────────────────────────────────────────────────────────


def _compress_lossy(
    header: bytes,
    triangles: np.ndarray,
) -> tuple[bytes, list[tuple[str, bytes]]]:
    all_verts = triangles[:, 3:].reshape(-1, 3)  # drop normals

    # Quantize float32 → uint16
    v_min = all_verts.min(axis=0)
    v_max = all_verts.max(axis=0)
    v_range = v_max - v_min
    v_range[v_range == 0] = 1

    quantized = ((all_verts - v_min) / v_range * 65535).astype(np.uint16)
    unique_q, inverse = np.unique(quantized, axis=0, return_inverse=True)
    indices = inverse.reshape(-1, 3).astype(np.int32)
    delta_q = np.diff(unique_q, axis=0, prepend=unique_q[:1]).astype(np.int32)

    meta = json.dumps(
        {
            "_format": "stl",
            "_mode": "lossy",
            "_n_tri": int(triangles.shape[0]),
            "_n_unique": int(unique_q.shape[0]),
            "_header_hex": header.hex(),
            "_v_min": v_min.tolist(),
            "_v_max": v_max.tolist(),
        }
    ).encode("utf-8")

    chunks = [
        # quantized verts as int32 delta — byte shuffle still helps
        ("zstd", _CCTX.compress(_byte_shuffle(delta_q.astype(np.float32)))),
        # indices
        ("zstd", _CCTX.compress(indices.tobytes())),
    ]

    return gzip.compress(meta, compresslevel=9), chunks
