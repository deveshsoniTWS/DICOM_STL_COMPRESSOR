# DICOM / STL Compressor (MedZip API)

Backend API for compressing and decompressing DICOM medical imaging files. Supports lossless and lossy compression.

## Prerequisites

- **Python 3.12+**
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Quick start

### 1. Clone the repo

```bash
git clone https://github.com/deveshsoniTWS/DICOM_STL_COMPRESSOR.git
cd DICOM_STL_COMPRESSOR
```

### 2. Go to the backend and install dependencies

**With uv (recommended):**

```bash
cd backend
uv sync
```

**With pip:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e .
```

### 3. Run the server

```bash
# From inside backend/
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or with pip/venv:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be at **http://localhost:8000**. Docs: **http://localhost:8000/docs**.

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/compress/dicom` | Upload `.dcm` → get `.medzip` (form: `file`, `mode`: `lossless` or `lossy`) |
| POST | `/decompress/dicom` | Upload `.medzip` → get reconstructed `.dcm` |
| POST | `/stats/dicom` | Upload `.dcm` → get compression stats only (no file back) |

### Example: compress a DICOM file

```bash
curl -X POST "http://localhost:8000/compress/dicom" \
  -F "file=@/path/to/your/image.dcm" \
  -F "mode=lossless" \
  -o compressed.medzip
```

### Example: decompress

```bash
curl -X POST "http://localhost:8000/decompress/dicom" \
  -F "file=@compressed.medzip" \
  -o reconstructed.dcm
```

## Project structure

```
DICOM_STL_COMPRESSOR/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── core.py          # Compress/decompress routing
│   ├── dicom/            # DICOM compress/decompress
│   ├── shared/           # Shared utilities
│   ├── stl/              # STL (future)
│   └── pyproject.toml
└── README.md
```

## License

See repository for license details.
