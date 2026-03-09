# MedZip Frontend

Next.js 15 frontend with Bun runtime for MedZip medical file compression.

## Project Structure

```
frontend/
├── app/
│   ├── components/          # React components
│   │   ├── Header.tsx       # Top navigation with operation toggle
│   │   ├── ProjectOverview.tsx  # Left sidebar info
│   │   ├── UploadZone.tsx   # Center drag & drop area
│   │   ├── MetricsPanel.tsx # Right stats panel
│   │   └── Footer.tsx       # Bottom status bar
│   ├── lib/
│   │   └── api.ts          # Backend API integration
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page with state management
│   └── globals.css         # Global styles
├── .env.local              # Environment variables
└── package.json
```

## Features

- 🎨 **Futuristic UI** - Hexagon patterns, glowing effects, glass panels
- 📁 **Drag & Drop** - Drop files directly into the hive
- 🗜️ **Compress** - DICOM (.dcm) and STL (.stl) files
- 📦 **Decompress** - .medzip files back to original format
- 🔄 **Dual Modes** - Lossless (70% avg) and Lossy Tactical (90% avg)
- 📊 **Real-time Stats** - Compression ratio, file sizes, frames/triangles
- ⚡ **Bun Runtime** - Blazing fast performance
- 🧩 **Component-based** - Clean, modular architecture

## Setup

```bash
# Install dependencies
bun install

# Configure backend URL (optional, defaults to localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
bun run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Backend

Make sure the backend is running:

```bash
cd ../backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. **Select Operation** - Click COMPRESS or DECOMPRESS in the header nav
2. **Choose Mode** (compress only) - Click Lossless or Lossy Tactical button
3. **Upload File** - Drag & drop or click "Browse Filesystem"
   - Compress: accepts .dcm or .stl files
   - Decompress: accepts .medzip files
4. **Process** - Click the compress/decompress button
5. **Download** - File downloads automatically, stats appear in right panel

## API Integration

The app uses a clean API layer (`lib/api.ts`) that:
- Handles all backend communication
- Extracts stats from response headers
- Manages file downloads
- Provides TypeScript types for type safety

## Tech Stack

- **Next.js 15** - App Router with React Server Components
- **React 19** - Latest React features
- **TypeScript** - Full type safety
- **Tailwind CSS 4** - Utility-first styling
- **Bun** - Fast JavaScript runtime and package manager

## Components

### Header
- Operation toggle (Compress/Decompress)
- Branding and navigation

### ProjectOverview
- Static project description
- Left sidebar content

### UploadZone
- Drag & drop file upload
- Mode selection (lossless/lossy)
- File processing trigger
- Hexagon pattern background

### MetricsPanel
- Static compression metrics
- Real-time processing stats
- Error display

### Footer
- System status
- Timestamp
- Branding info
