"""
shared/format.py
.medzip binary format — pack and unpack.

Layout:
  [4B]  Magic: "MZIP"
  [1B]  Mode: 0=lossless, 1=lossy
  [1B]  Format: 0=dicom, 1=stl
  [1B]  Is multiframe: 0=no, 1=yes
  [4B]  Metadata length
  [NB]  gzip-compressed metadata
  [4B]  Number of chunks
  per chunk:
    [1B]  Codec: 0=jpeg2000, 1=zstd
    [4B]  Chunk length
    [NB]  Compressed frame bytes
"""

import io
import struct

MAGIC = b"MZIP"
MODE_LOSSLESS = 0
MODE_LOSSY = 1
FMT_DICOM = 0
FMT_STL = 1
CODEC_J2K = 0
CODEC_ZSTD = 1


def pack(
    mode: str,
    fmt: str,
    meta_compressed: bytes,
    chunks: list[tuple[str, bytes]],
) -> bytes:
    buf = io.BytesIO()
    buf.write(MAGIC)
    buf.write(struct.pack("B", MODE_LOSSLESS if mode == "lossless" else MODE_LOSSY))
    buf.write(struct.pack("B", FMT_DICOM if fmt == "dicom" else FMT_STL))
    buf.write(struct.pack("B", 1 if len(chunks) > 1 else 0))
    buf.write(struct.pack(">I", len(meta_compressed)))
    buf.write(meta_compressed)
    buf.write(struct.pack(">I", len(chunks)))
    for codec, data in chunks:
        buf.write(struct.pack("B", CODEC_J2K if codec == "j2k" else CODEC_ZSTD))
        buf.write(struct.pack(">I", len(data)))
        buf.write(data)
    return buf.getvalue()


def unpack(data: bytes) -> tuple[str, str, bytes, list[tuple[str, bytes]]]:
    buf = io.BytesIO(data)
    magic = buf.read(4)
    if magic != MAGIC:
        raise ValueError(f"Invalid .medzip file — bad magic: {magic}")

    mode_byte = struct.unpack("B", buf.read(1))[0]
    mode = "lossless" if mode_byte == MODE_LOSSLESS else "lossy"
    fmt_byte = struct.unpack("B", buf.read(1))[0]
    fmt = "dicom" if fmt_byte == FMT_DICOM else "stl"
    _ = buf.read(1)  # is_multiframe — informational

    meta_len = struct.unpack(">I", buf.read(4))[0]
    meta_compressed = buf.read(meta_len)

    n_chunks = struct.unpack(">I", buf.read(4))[0]
    chunks: list[tuple[str, bytes]] = []
    for _ in range(n_chunks):
        codec_byte = struct.unpack("B", buf.read(1))[0]
        codec = "j2k" if codec_byte == CODEC_J2K else "zstd"
        chunk_len = struct.unpack(">I", buf.read(4))[0]
        chunks.append((codec, buf.read(chunk_len)))

    return mode, fmt, meta_compressed, chunks
