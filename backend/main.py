import os
import tempfile
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from core import compress, decompress


class CompressionMode(str, Enum):
    lossless = "lossless"
    lossy = "lossy"


app = FastAPI(title="MedZip API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {"status": "MedZip API running", "version": "3.0.0"}


def _detect_format(filename: str) -> str:
    """Detect file format from extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".dcm":
        return "dicom"
    elif ext == ".stl":
        return "stl"
    elif ext == ".medzip":
        return "medzip"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: .dcm, .stl, .medzip",
        )


# ─── UNIFIED ENDPOINTS ────────────────────────────────────────────────────────


@app.post("/compress")
async def compress_file(
    file: UploadFile = File(...),
    mode: CompressionMode = Form(default=CompressionMode.lossless),
) -> Response:
    """Upload a .dcm or .stl file → returns .medzip compressed file."""
    filename = file.filename or "unknown"
    fmt = _detect_format(filename)

    if fmt == "medzip":
        raise HTTPException(status_code=400, detail="Cannot compress .medzip files")

    suffix = ".dcm" if fmt == "dicom" else ".stl"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        compressed_bytes, stats = compress(tmp_path, fmt=fmt, mode=mode.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

    output_filename = filename.replace(suffix, f"_{mode.value}.medzip")

    # Build headers based on format
    headers = {
        "Content-Disposition": f"attachment; filename={output_filename}",
        "X-Original-Size-KB": str(stats["original_size_kb"]),
        "X-Compressed-Size-KB": str(stats["compressed_size_kb"]),
        "X-Compression-Ratio": str(stats["compression_ratio_pct"]),
        "X-Mode": mode.value,
        "X-Format": fmt.upper(),
    }

    if fmt == "dicom":
        headers["X-Frames"] = str(stats["n_frames"])
        expose_headers = "X-Original-Size-KB, X-Compressed-Size-KB, X-Compression-Ratio, X-Mode, X-Format, X-Frames"
    else:  # stl
        headers["X-Triangles"] = str(stats["n_triangles"])
        expose_headers = "X-Original-Size-KB, X-Compressed-Size-KB, X-Compression-Ratio, X-Mode, X-Format, X-Triangles"

    headers["Access-Control-Expose-Headers"] = expose_headers

    return Response(
        content=compressed_bytes,
        media_type="application/octet-stream",
        headers=headers,
    )


@app.post("/decompress")
async def decompress_file(file: UploadFile = File(...)) -> Response:
    """Upload a .medzip file → returns reconstructed .dcm or .stl file."""
    filename = file.filename or "unknown"
    fmt_check = _detect_format(filename)

    if fmt_check != "medzip":
        raise HTTPException(
            status_code=400, detail="Only .medzip files can be decompressed"
        )

    data = await file.read()

    # Try to detect format from the medzip content
    try:
        # Peek at the format by attempting decompress
        from shared.format import unpack

        _, fmt, _, _ = unpack(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid .medzip file: {str(e)}")

    try:
        if fmt == "dicom":
            file_bytes, internal = decompress(data, fmt="dicom")
            output_ext = ".dcm"
            mode = internal.get("_mode", "unknown")
            shape = internal.get("_shape", [])
            n_frames = shape[0] if len(shape) == 3 else 1
            format_specific_header = ("X-Frames", str(n_frames))
            expose_extra = "X-Frames"
        else:  # stl
            file_bytes, meta = decompress(data, fmt="stl")
            output_ext = ".stl"
            mode = meta.get("_mode", "unknown")
            n_triangles = meta.get("_n_tri", 0)
            format_specific_header = ("X-Triangles", str(n_triangles))
            expose_extra = "X-Triangles"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    output_filename = filename.replace(".medzip", f"_decompressed{output_ext}")
    compressed_size_kb = round(len(data) / 1024, 2)
    decompressed_size_kb = round(len(file_bytes) / 1024, 2)

    headers = {
        "Content-Disposition": f"attachment; filename={output_filename}",
        "X-Compressed-Size-KB": str(compressed_size_kb),
        "X-Decompressed-Size-KB": str(decompressed_size_kb),
        "X-Mode": mode,
        "X-Format": fmt.upper(),
        format_specific_header[0]: format_specific_header[1],
        "Access-Control-Expose-Headers": f"X-Compressed-Size-KB, X-Decompressed-Size-KB, X-Mode, X-Format, {expose_extra}",
    }

    return Response(
        content=file_bytes,
        media_type="application/octet-stream",
        headers=headers,
    )
