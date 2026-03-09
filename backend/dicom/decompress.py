"""
dicom/decompress.py
DICOM decompression from .medzip bytes.
Reconstructs a proper .dcm file.
"""

import io

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from shared.format import unpack
from shared.metadata import decompress_meta
from shared.parallel import decompress_frames
from shared.pixels import decompress_frame


def decompress(data: bytes) -> tuple[bytes, dict]:
    """
    Decompress a .medzip file back to a proper .dcm file.

    Returns:
        (dcm_bytes, metadata_dict)
    """
    mode, fmt, meta_compressed, chunks = unpack(data)

    if fmt != "dicom":
        raise ValueError(f"Expected dicom format, got: {fmt}")

    meta_dict = decompress_meta(meta_compressed)
    shape = tuple(int(x) for x in meta_dict.get("_shape", []))
    dtype: str = meta_dict.get("_dtype", "uint8")
    is_multiframe = len(shape) == 3

    if is_multiframe:
        frame_shape = (shape[1], shape[2])
        pixel_array = decompress_frames(chunks, mode, frame_shape, dtype)
    else:
        codec, chunk_data = chunks[0]
        pixel_array = decompress_frame(codec, chunk_data, mode, shape, dtype)

    dcm_bytes = _rebuild_dicom(pixel_array, meta_dict)
    return dcm_bytes, meta_dict


# ─── HELPERS ──────────────────────────────────────────────────────────────────

# Tags we safely restore — only ones with predictable string representation
_SAFE_TAGS = {
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "StudyDate",
    "StudyTime",
    "StudyDescription",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "SOPInstanceUID",
    "SOPClassUID",
    "Modality",
    "InstitutionName",
    "Manufacturer",
    "PhotometricInterpretation",
    "WindowCenter",
    "WindowWidth",
    "RescaleIntercept",
    "RescaleSlope",
    "ImageType",
}


def _rebuild_dicom(pixel_array: np.ndarray, meta_dict: dict) -> bytes:
    """Reconstruct a valid .dcm file from pixel array + metadata dict."""

    # ── File meta ─────────────────────────────────────────────────────────────
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = meta_dict.get(
        "SOPClassUID", "1.2.840.10008.5.1.4.1.1.2"
    )
    file_meta.MediaStorageSOPInstanceUID = meta_dict.get(
        "SOPInstanceUID", generate_uid()
    )
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()

    # ── Dataset ───────────────────────────────────────────────────────────────
    ds = FileDataset(
        filename_or_obj="",
        dataset=Dataset(),
        file_meta=file_meta,
        preamble=b"\x00" * 128,  # required 128-byte preamble
    )

    # Restore only safe string tags — avoids VR type mismatch warnings
    for tag in _SAFE_TAGS:
        if tag in meta_dict and tag not in ("_shape", "_mode", "_dtype", "_file_meta"):
            try:
                setattr(ds, tag, meta_dict[tag])
            except Exception:
                pass

    # ── Pixel tags — set explicitly with correct types ────────────────────────
    if pixel_array.ndim == 3:
        ds.NumberOfFrames = pixel_array.shape[0]
        ds.Rows = pixel_array.shape[1]
        ds.Columns = pixel_array.shape[2]
    else:
        ds.Rows = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]

    ds.BitsAllocated = 8 if pixel_array.dtype == np.uint8 else 16
    ds.BitsStored = 8 if pixel_array.dtype == np.uint8 else 16
    ds.HighBit = 7 if pixel_array.dtype == np.uint8 else 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PixelData = pixel_array.tobytes()

    if not hasattr(ds, "PhotometricInterpretation"):
        ds.PhotometricInterpretation = "MONOCHROME2"

    # ── Write ─────────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    pydicom.dcmwrite(buf, ds, write_like_original=False)
    return buf.getvalue()
