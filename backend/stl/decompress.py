"""
stl/decompress.py
STL decompression from .medzip bytes — fully vectorized.
"""

import gzip
import io
import json
import struct

import numpy as np
import zstandard as zstd

from shared.format import unpack

_DCTX = zstd.ZstdDecompressor()


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


# ─── BYTE UNSHUFFLE ───────────────────────────────────────────────────────────


def _byte_unshuffle(data: bytes, n: int) -> np.ndarray:
    """
    Reverse byte shuffle → reconstruct float32 array.
    n = total number of floats expected.
    """
    b = np.frombuffer(data, dtype=np.uint8).reshape(4, n)
    return np.frombuffer(b.T.copy().tobytes(), dtype=np.float32)


# ─── LOSSLESS ─────────────────────────────────────────────────────────────────


def _decompress_lossless(meta: dict, chunks: list[tuple[str, bytes]]) -> bytes:
    n_tri = meta["_n_tri"]
    n_unique = meta["_n_unique"]
    header = bytes.fromhex(meta["_header_hex"])

    normals = _byte_unshuffle(_DCTX.decompress(chunks[0][1]), n_tri * 3).reshape(
        n_tri, 3
    )
    delta_verts = _byte_unshuffle(_DCTX.decompress(chunks[1][1]), n_unique * 3).reshape(
        n_unique, 3
    )
    indices = np.frombuffer(_DCTX.decompress(chunks[2][1]), dtype=np.int32).reshape(
        n_tri, 3
    )

    unique_verts = np.cumsum(delta_verts, axis=0)
    all_verts = unique_verts[indices]  # (N, 3, 3)

    return _write_stl(header, normals, all_verts)


# ─── LOSSY ────────────────────────────────────────────────────────────────────


def _decompress_lossy(meta: dict, chunks: list[tuple[str, bytes]]) -> bytes:
    n_tri = meta["_n_tri"]
    n_unique = meta["_n_unique"]
    header = bytes.fromhex(meta["_header_hex"])
    v_min = np.array(meta["_v_min"], dtype=np.float32)
    v_max = np.array(meta["_v_max"], dtype=np.float32)
    v_range = v_max - v_min
    v_range[v_range == 0] = 1

    delta_q_f = _byte_unshuffle(_DCTX.decompress(chunks[0][1]), n_unique * 3).reshape(
        n_unique, 3
    )
    delta_q = delta_q_f.view(np.int32)  # reinterpret as int32
    indices = np.frombuffer(_DCTX.decompress(chunks[1][1]), dtype=np.int32).reshape(
        n_tri, 3
    )

    unique_q = np.cumsum(delta_q, axis=0).astype(np.uint16)
    unique_verts = (unique_q.astype(np.float32) / 65535.0) * v_range + v_min
    all_verts = unique_verts[indices]  # (N, 3, 3)

    # Recompute normals via vectorized cross product
    e1 = all_verts[:, 1] - all_verts[:, 0]
    e2 = all_verts[:, 2] - all_verts[:, 0]
    normals = np.cross(e1, e2).astype(np.float32)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normals = normals / norms

    return _write_stl(header, normals, all_verts)


# ─── WRITE ────────────────────────────────────────────────────────────────────


def _write_stl(
    header: bytes,
    normals: np.ndarray,  # (N, 3) float32
    all_verts: np.ndarray,  # (N, 3, 3) float32
) -> bytes:
    """Write binary STL — fully vectorized via structured numpy array."""
    n_tri = normals.shape[0]

    dtype = np.dtype(
        [
            ("normal", np.float32, (3,)),
            ("v0", np.float32, (3,)),
            ("v1", np.float32, (3,)),
            ("v2", np.float32, (3,)),
            ("attr", np.uint16),
        ]
    )
    out = np.zeros(n_tri, dtype=dtype)
    out["normal"] = normals.astype(np.float32)
    out["v0"] = all_verts[:, 0].astype(np.float32)
    out["v1"] = all_verts[:, 1].astype(np.float32)
    out["v2"] = all_verts[:, 2].astype(np.float32)

    buf = io.BytesIO()
    buf.write(header.ljust(80, b"\x00")[:80])
    buf.write(struct.pack("<I", n_tri))
    buf.write(out.tobytes())

    return buf.getvalue()
