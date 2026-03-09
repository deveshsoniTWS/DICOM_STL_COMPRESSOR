"""
shared/metadata.py
DICOM metadata extraction, compression, decompression.

Uses pickle to serialize the pydicom Dataset — preserves all VR types
perfectly without any string conversion or binary format hacks.
Then gzips the result for size.
"""

import gzip
import json
import pickle
import struct

import pydicom
from pydicom.dataset import Dataset
from pydicom.tag import Tag

PIXEL_DATA_TAG = Tag(0x7FE0, 0x0010)


def extract(ds: pydicom.Dataset) -> Dataset:
    """Extract all tags except PixelData into a new Dataset."""
    meta = Dataset()
    for elem in ds:
        if elem.tag == PIXEL_DATA_TAG:
            continue
        meta.add(elem)
    return meta


def compress_meta(meta: Dataset, pixel_shape: list, mode: str, dtype: str) -> bytes:
    """
    Serialize dataset via pickle → gzip.
    Internal fields stored as JSON header before the pickle bytes.

    Layout: [4B internal_len][internal JSON][pickle bytes] → gzip
    """
    internal = json.dumps(
        {
            "_shape": pixel_shape,
            "_mode": mode,
            "_dtype": dtype,
        }
    ).encode("utf-8")

    ds_bytes = pickle.dumps(meta, protocol=pickle.HIGHEST_PROTOCOL)
    packed = struct.pack(">I", len(internal)) + internal + ds_bytes

    return gzip.compress(packed, compresslevel=9)


def decompress_meta(data: bytes) -> tuple[Dataset, dict]:
    """
    gzip decompress → unpack internal fields + unpickle dataset.

    Returns:
        (dataset, internal_dict)
        internal_dict has _shape, _mode, _dtype
    """
    raw = gzip.decompress(data)
    int_len = struct.unpack(">I", raw[:4])[0]
    internal = json.loads(raw[4 : 4 + int_len].decode("utf-8"))
    ds_bytes = raw[4 + int_len :]
    ds = pickle.loads(ds_bytes)

    return ds, internal
