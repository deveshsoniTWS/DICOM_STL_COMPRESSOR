import os
import tempfile
from enum import Enum

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


@app.post("/compress/dicom")
async def compress_dicom(
    file: UploadFile = File(...),
    mode: CompressionMode = Form(default=CompressionMode.lossless),
) -> Response:
    with tempfile.NamedTemporaryFile(suffix=".dcm", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        compressed_bytes, stats = compress(tmp_path, fmt="dicom", mode=mode.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

    original_name = file.filename or "output.dcm"
    filename = original_name.replace(".dcm", f"_{mode.value}.medzip")

    return Response(
        content=compressed_bytes,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Original-Size-KB": str(stats["original_size_kb"]),
            "X-Compressed-Size-KB": str(stats["compressed_size_kb"]),
            "X-Compression-Ratio": str(stats["compression_ratio_pct"]),
            "X-Mode": mode.value,
            "X-Frames": str(stats["n_frames"]),
            "Access-Control-Expose-Headers": (
                "X-Original-Size-KB, X-Compressed-Size-KB, "
                "X-Compression-Ratio, X-Mode, X-Frames"
            ),
        },
    )


@app.post("/decompress/dicom")
async def decompress_dicom(file: UploadFile = File(...)) -> Response:
    """Upload a .medzip file → returns reconstructed .dcm file."""
    data = await file.read()
    try:
        dcm_bytes, _ = decompress(data, fmt="dicom")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    original_name = file.filename or "output.medzip"
    filename = original_name.replace(".medzip", "_decompressed.dcm")

    return Response(
        content=dcm_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/stats/dicom")
async def stats_only(
    file: UploadFile = File(...),
    mode: CompressionMode = Form(default=CompressionMode.lossless),
) -> JSONResponse:
    """Upload a .dcm file → returns compression stats only."""
    with tempfile.NamedTemporaryFile(suffix=".dcm", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        _, stats = compress(tmp_path, fmt="dicom", mode=mode.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

    return JSONResponse(stats)
