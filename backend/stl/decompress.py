"""

stl/decompress.py

STL decompression — fully vectorized.

Normals recomputed from geometry via cross product (both modes).

"""
 
import gzip

import io

import json

import struct

import numpy as np

import zstandard as zstd
 
from shared.format import unpack
 
_DCTX = zstd.ZstdDecompressor()

PRECISION = 1_000_000
 
 
def decompress(data: bytes) -> tuple[bytes, dict]:

    mode, fmt, meta_compressed, chunks = unpack(data)
 
    if fmt != "stl":

        raise ValueError(f"Expected stl format, got: {fmt}")
 
    meta = json.loads(gzip.decompress(meta_compressed).decode("utf-8"))
 
    if mode == "lossless":

        stl_bytes = _decompress_lossless(meta, chunks)

    else:

        stl_bytes = _decompress_lossy(meta, chunks)
 
    return stl_bytes, meta
 
 
# ─── SHARED: recompute normals ────────────────────────────────────────────────
 
def _recompute_normals(all_verts: np.ndarray) -> np.ndarray:

    """Vectorized cross product normals from (N, 3, 3) vertex array."""

    e1      = all_verts[:, 1] - all_verts[:, 0]

    e2      = all_verts[:, 2] - all_verts[:, 0]

    normals = np.cross(e1, e2).astype(np.float32)

    norms   = np.linalg.norm(normals, axis=1, keepdims=True)

    norms[norms == 0] = 1

    return normals / norms
 
 
# ─── LOSSLESS ─────────────────────────────────────────────────────────────────
 
def _decompress_lossless(meta: dict, chunks: list[tuple[str, bytes]]) -> bytes:

    n_tri    = meta["_n_tri"]

    n_unique = meta["_n_unique"]

    header   = bytes.fromhex(meta["_header_hex"])
 
    deltas  = np.frombuffer(_DCTX.decompress(chunks[0][1]), dtype=np.int64).reshape(n_unique, 3)

    indices = np.frombuffer(_DCTX.decompress(chunks[1][1]), dtype=np.int32).reshape(n_tri,    3)
 
    int_verts    = np.cumsum(deltas, axis=0)

    unique_verts = (int_verts.astype(np.float64) / PRECISION).astype(np.float32)

    all_verts    = unique_verts[indices]  # (N, 3, 3)

    normals      = _recompute_normals(all_verts)
 
    return _write_stl(header, normals, all_verts)
 
 
# ─── LOSSY ────────────────────────────────────────────────────────────────────
 
def _decompress_lossy(meta: dict, chunks: list[tuple[str, bytes]]) -> bytes:

    n_tri    = meta["_n_tri"]

    n_unique = meta["_n_unique"]

    header   = bytes.fromhex(meta["_header_hex"])

    v_min    = np.array(meta["_v_min"], dtype=np.float32)

    v_max    = np.array(meta["_v_max"], dtype=np.float32)

    v_range  = v_max - v_min

    v_range[v_range == 0] = 1
 
    deltas  = np.frombuffer(_DCTX.decompress(chunks[0][1]), dtype=np.int64).reshape(n_unique, 3)

    indices = np.frombuffer(_DCTX.decompress(chunks[1][1]), dtype=np.int32).reshape(n_tri,    3)
 
    int_verts    = np.cumsum(deltas, axis=0)

    unique_q     = (int_verts.astype(np.float64) / PRECISION).astype(np.uint16)

    unique_verts = (unique_q.astype(np.float32) / 65535.0) * v_range + v_min

    all_verts    = unique_verts[indices]

    normals      = _recompute_normals(all_verts)
 
    return _write_stl(header, normals, all_verts)
 
 
# ─── WRITE ────────────────────────────────────────────────────────────────────
 
def _write_stl(

    header: bytes,

    normals: np.ndarray,    # (N, 3) float32

    all_verts: np.ndarray,  # (N, 3, 3) float32

) -> bytes:

    n_tri  = normals.shape[0]

    dtype  = np.dtype([

        ("normal", np.float32, (3,)),

        ("v0",     np.float32, (3,)),

        ("v1",     np.float32, (3,)),

        ("v2",     np.float32, (3,)),

        ("attr",   np.uint16),

    ])

    out           = np.zeros(n_tri, dtype=dtype)

    out["normal"] = normals.astype(np.float32)

    out["v0"]     = all_verts[:, 0].astype(np.float32)

    out["v1"]     = all_verts[:, 1].astype(np.float32)

    out["v2"]     = all_verts[:, 2].astype(np.float32)
 
    buf = io.BytesIO()

    buf.write(header.ljust(80, b"\x00")[:80])

    buf.write(struct.pack("<I", n_tri))

    buf.write(out.tobytes())

    return buf.getvalue()
 