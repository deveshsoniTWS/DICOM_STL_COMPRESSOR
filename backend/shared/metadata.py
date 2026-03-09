"""
shared/metadata.py
DICOM metadata extraction, compression, decompression.
"""

import gzip
import json

import pydicom


def extract(ds: pydicom.Dataset) -> dict:
    """Extract all DICOM tags into a plain dict. Skips PixelData."""
    meta: dict = {}
    for elem in ds:
        if elem.keyword in ("PixelData", ""):
            continue
        try:
            val = elem.value
            if hasattr(val, "__iter__") and not isinstance(val, (str, bytes)):
                val = [str(v) for v in val]
            else:
                val = str(val)
            meta[elem.keyword] = val
        except Exception:
            pass

    if hasattr(ds, "file_meta"):
        meta["_file_meta"] = {}
        for elem in ds.file_meta:
            try:
                meta["_file_meta"][elem.keyword] = str(elem.value)
            except Exception:
                pass

    return meta


def compress_meta(meta: dict) -> bytes:
    raw = json.dumps(meta, ensure_ascii=False).encode("utf-8")
    return gzip.compress(raw, compresslevel=9)


def decompress_meta(data: bytes) -> dict:
    raw = gzip.decompress(data)
    return json.loads(raw.decode("utf-8"))
