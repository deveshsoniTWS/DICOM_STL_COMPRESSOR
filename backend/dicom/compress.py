"""
dicom/compress.py
DICOM compression — lossless and lossy modes.
"""

import os

import pydicom

from shared.format import pack
from shared.metadata import compress_meta, extract
from shared.parallel import compress_frames
from shared.pixels import compress_frame


def compress(dicom_path: str, mode: str) -> tuple[bytes, dict]:
    """
    Compress a DICOM file into .medzip bytes.

    Args:
        dicom_path: path to .dcm file
        mode:       'lossless' or 'lossy'

    Returns:
        (compressed_bytes, stats_dict)
    """
    # 1. Read DICOM
    ds = pydicom.dcmread(dicom_path)
    pixel_array = ds.pixel_array

    # 2. Metadata
    meta_dict = extract(ds)
    meta_dict["_shape"] = list(pixel_array.shape)
    meta_dict["_mode"] = mode
    meta_dict["_dtype"] = str(pixel_array.dtype)
    meta_compressed = compress_meta(meta_dict)

    # 3. Pixels
    is_multiframe = pixel_array.ndim == 3
    if is_multiframe:
        chunks = compress_frames(pixel_array, mode)
    else:
        chunks = [compress_frame(pixel_array, mode)]

    # 4. Pack
    compressed_bytes = pack(mode, "dicom", meta_compressed, chunks)

    # 5. Stats
    original_size = os.path.getsize(dicom_path)
    compressed_size = len(compressed_bytes)
    ratio = round((1 - compressed_size / original_size) * 100, 2)

    stats = {
        "original_size_kb": round(original_size / 1024, 2),
        "compressed_size_kb": round(compressed_size / 1024, 2),
        "compression_ratio_pct": ratio,
        "mode": mode,
        "format": "DICOM",
        "is_multiframe": is_multiframe,
        "n_frames": pixel_array.shape[0] if is_multiframe else 1,
        "shape": list(pixel_array.shape),
        "dtype": str(pixel_array.dtype),
    }

    return compressed_bytes, stats
