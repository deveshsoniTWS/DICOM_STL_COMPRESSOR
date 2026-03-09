"""
dicom/decompress.py
DICOM decompression from .medzip bytes.
Reconstructs a proper .dcm file.
"""

import io

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import UID, ExplicitVRLittleEndian, generate_uid

from shared.format import unpack
from shared.metadata import decompress_meta
from shared.parallel import decompress_frames
from shared.pixels import decompress_frame


def decompress(data: bytes) -> tuple[bytes, dict]:
    """
    Decompress a .medzip file back to a proper .dcm file.

    Returns:
        (dcm_bytes, internal_dict)
    """
    mode, fmt, meta_compressed, chunks = unpack(data)

    if fmt != "dicom":
        raise ValueError(f"Expected dicom format, got: {fmt}")

    meta_ds, internal = decompress_meta(meta_compressed)
    shape = tuple(int(x) for x in internal.get("_shape", []))
    dtype: str = internal.get("_dtype", "uint8")
    is_multiframe = len(shape) == 3

    if is_multiframe:
        frame_shape = (shape[1], shape[2])
        pixel_array = decompress_frames(chunks, mode, frame_shape, dtype)
    else:
        codec, chunk_data = chunks[0]
        pixel_array = decompress_frame(codec, chunk_data, mode, shape, dtype)

    dcm_bytes = _rebuild_dicom(pixel_array, meta_ds)
    return dcm_bytes, internal


def _rebuild_dicom(pixel_array: np.ndarray, meta_ds: pydicom.Dataset) -> bytes:
    """Reconstruct a valid .dcm file from pixel array + original Dataset."""
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = UID(
        getattr(meta_ds, "SOPClassUID", "1.2.840.10008.5.1.4.1.1.2")
    )
    file_meta.MediaStorageSOPInstanceUID = UID(
        getattr(meta_ds, "SOPInstanceUID", generate_uid())
    )
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = UID(generate_uid())

    ds = FileDataset(
        filename_or_obj="",
        dataset=meta_ds,
        file_meta=file_meta,
        preamble=b"\x00" * 128,
    )

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

    buf = io.BytesIO()
    pydicom.dcmwrite(buf, ds, write_like_original=False)
    return buf.getvalue()
