# MedZip Frontend

Next.js 15 frontend with Bun runtime for MedZip medical file compression.

## Features

- 🎨 Futuristic UI with hexagon patterns and glowing effects
- 📁 Drag & drop file upload
- 🗜️ Compress DICOM (.dcm) and STL (.stl) files
- 📦 Decompress .medzip files
- 🔄 Lossless and lossy compression modes
- 📊 Real-time stats display (compression ratio, file sizes, etc.)
- ⚡ Built with Bun for blazing fast performance

## Run locally

```bash
# Install dependencies
bun install

# Run dev server
bun run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Backend

Make sure the backend is running on `http://localhost:8000`:

```bash
cd ../backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. Select operation (COMPRESS or DECOMPRESS in nav)
2. For compression, choose mode (Lossless or Lossy Tactical)
3. Drag & drop or browse for file (.dcm, .stl, or .medzip)
4. Click process button
5. File downloads automatically with stats displayed in the metrics panel

## Tech Stack

- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS 4
- Bun runtime
