"""
core.py
Single entry point for main.py.
Routes compress/decompress to the right format handler.
"""

from dicom.compress import compress as dicom_compress
from dicom.decompress import decompress as dicom_decompress
from stl.compress import compress as stl_compress
from stl.decompress import decompress as stl_decompress


def compress(file_path: str, fmt: str, mode: str) -> tuple[bytes, dict]:
    if mode not in ("lossless", "lossy"):
        raise ValueError("mode must be 'lossless' or 'lossy'")
    if fmt == "dicom":
        return dicom_compress(file_path, mode)
    if fmt == "stl":
        return stl_compress(file_path, mode)
    raise ValueError(f"Unsupported format: {fmt}")


def decompress(data: bytes, fmt: str) -> tuple[bytes, dict]:
    if fmt == "dicom":
        return dicom_decompress(data)
    if fmt == "stl":
        return stl_decompress(data)
    raise ValueError(f"Unsupported format: {fmt}")
