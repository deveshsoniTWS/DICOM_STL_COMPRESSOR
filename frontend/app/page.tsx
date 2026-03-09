'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<'lossless' | 'lossy'>('lossless');
  const [operation, setOperation] = useState<'compress' | 'decompress'>('compress');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStats(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setStats(null);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (operation === 'compress') {
        formData.append('mode', mode);
      }

      const endpoint = operation === 'compress' ? '/compress' : '/decompress';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Operation failed');
      }

      const extractedStats: any = {
        format: response.headers.get('X-Format'),
        mode: response.headers.get('X-Mode'),
      };

      if (operation === 'compress') {
        extractedStats.originalSizeKB = response.headers.get('X-Original-Size-KB');
        extractedStats.compressedSizeKB = response.headers.get('X-Compressed-Size-KB');
        extractedStats.compressionRatio = response.headers.get('X-Compression-Ratio');
        extractedStats.frames = response.headers.get('X-Frames');
        extractedStats.triangles = response.headers.get('X-Triangles');
      } else {
        extractedStats.compressedSizeKB = response.headers.get('X-Compressed-Size-KB');
        extractedStats.decompressedSizeKB = response.headers.get('X-Decompressed-Size-KB');
        extractedStats.frames = response.headers.get('X-Frames');
        extractedStats.triangles = response.headers.get('X-Triangles');
      }

      setStats(extractedStats);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'output';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col overflow-x-hidden bg-[#0a0f12]">
      {/* Grid Background */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(46, 204, 112, 0.05) 1px, transparent 0)',
        backgroundSize: '40px 40px'
      }}></div>

      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-[#2ecc70]/10 rounded-full blur-[120px]"></div>
        <div className="absolute top-1/2 -right-24 w-[500px] h-[500px] bg-[#8b5cf6]/10 rounded-full blur-[150px]"></div>
      </div>

      {/* Header */}
      <header className="flex items-center justify-between px-6 lg:px-20 py-6 border-b border-[#2ecc70]/10 backdrop-blur-xl bg-[#0f172a]/60 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="size-8 bg-gradient-to-br from-[#2ecc70] to-[#8b5cf6] flex items-center justify-center rounded-lg shadow-lg shadow-[#2ecc70]/20">
            <span className="text-[#0a0f12] text-xl font-bold">⬡</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight uppercase">MedZip</h2>
        </div>
        <nav className="hidden md:flex items-center gap-10">
          <button
            onClick={() => setOperation('compress')}
            className={`text-[11px] uppercase tracking-[0.2em] font-medium transition-colors ${
              operation === 'compress' ? 'text-[#2ecc70]' : 'text-slate-400 hover:text-[#2ecc70]'
            }`}
          >
            COMPRESS
          </button>
          <button
            onClick={() => setOperation('decompress')}
            className={`text-[11px] uppercase tracking-[0.2em] font-medium transition-colors ${
              operation === 'decompress' ? 'text-[#2ecc70]' : 'text-slate-400 hover:text-[#2ecc70]'
            }`}
          >
            DECOMPRESS
          </button>
        </nav>
        <div className="flex items-center gap-6">
          <button className="px-5 py-2 bg-[#2ecc70]/10 hover:bg-[#2ecc70]/20 border border-[#2ecc70]/30 rounded-full text-[10px] font-bold uppercase tracking-widest text-[#2ecc70] transition-all">
            BumbleBeeDev
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 lg:px-20 py-12 gap-12 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start w-full">
          {/* Left: Project Overview */}
          <div className="lg:col-span-3 flex flex-col gap-8 pt-12">
            <div className="space-y-6">
              <div className="flex items-center gap-2">
                <span className="h-px w-8 bg-[#2ecc70]"></span>
                <span className="text-[10px] uppercase tracking-[0.3em] text-[#2ecc70] font-bold">Project Overview</span>
              </div>
              <p className="text-sm leading-relaxed text-slate-300 font-light border-l border-[#2ecc70]/20 pl-4">
                <span className="text-[#2ecc70] font-bold">MedZip</span> is designed to simplify the handling of large DICOM and STL files. The platform provides an easy way to compress and decompress files while maintaining important data and visual quality.
              </p>
              <div className="flex items-center gap-2 pt-4 opacity-50">
                <span className="h-px w-4 bg-[#8b5cf6]"></span>
                <span className="text-[9px] uppercase tracking-[0.2em] text-[#8b5cf6] font-mono italic">End of Summary</span>
              </div>
            </div>
          </div>

          {/* Center: Drag & Drop */}
          <div className="lg:col-span-6 flex flex-col items-center gap-8">
            <div className="w-full aspect-square max-w-[500px] relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#2ecc70] via-[#8b5cf6] to-[#2ecc70] rounded-3xl opacity-20 group-hover:opacity-40 blur transition-opacity duration-500"></div>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="relative w-full h-full backdrop-blur-xl bg-[#0f172a]/60 border border-[#2ecc70]/10 rounded-3xl border-2 border-dashed border-[#2ecc70]/30 flex flex-col items-center justify-center p-12 overflow-hidden"
              >
                {/* Hexagon Pattern */}
                <div className="absolute inset-0 opacity-10 pointer-events-none" style={{
                  backgroundImage: `linear-gradient(30deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                    linear-gradient(150deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                    linear-gradient(30deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                    linear-gradient(150deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                    linear-gradient(60deg, #2ecc70 25%, transparent 25.5%, transparent 75%, #2ecc70 75%, #2ecc70),
                    linear-gradient(60deg, #2ecc70 25%, transparent 25.5%, transparent 75%, #2ecc70 75%, #2ecc70)`,
                  backgroundSize: '80px 140px'
                }}></div>

                <div className="z-10 flex flex-col items-center text-center gap-6">
                  <div className="size-24 rounded-full bg-[#2ecc70]/20 flex items-center justify-center ring-8 ring-[#2ecc70]/5 group-hover:scale-110 transition-transform duration-500">
                    <span className="text-[#2ecc70] text-5xl">📁</span>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold tracking-tight text-white mb-2">
                      {operation === 'compress' ? 'Initialize Hive Transfer' : 'Decompress Archive'}
                    </h3>
                    <p className="text-slate-400 text-sm max-w-[280px]">
                      {operation === 'compress' 
                        ? 'Drop DICOM slices or STL mesh files to begin tactical processing'
                        : 'Drop .medzip files to restore original format'}
                    </p>
                  </div>
                  {file && (
                    <div className="text-sm text-[#2ecc70] font-mono">
                      {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </div>
                  )}
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept={operation === 'compress' ? '.dcm,.stl' : '.medzip'}
                    className="hidden"
                    id="file-input"
                  />
                  <label
                    htmlFor="file-input"
                    className="mt-4 px-8 py-3 bg-[#2ecc70] text-[#0a0f12] font-bold rounded-lg shadow-xl shadow-[#2ecc70]/20 hover:scale-105 transition-transform cursor-pointer"
                  >
                    Browse Filesystem
                  </label>
                  {file && (
                    <button
                      onClick={handleSubmit}
                      disabled={loading}
                      className="px-8 py-3 bg-[#8b5cf6] text-white font-bold rounded-lg shadow-xl shadow-[#8b5cf6]/20 hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Processing...' : operation === 'compress' ? 'Compress' : 'Decompress'}
                    </button>
                  )}
                </div>

                <div className="absolute top-6 left-6 text-[9px] font-mono text-[#2ecc70]/50">ENC_0x4429</div>
                <div className="absolute bottom-6 right-6 text-[9px] font-mono text-[#2ecc70]/50">SEC_READY</div>
              </div>
            </div>

            {/* Mode Selection (only for compress) */}
            {operation === 'compress' && (
              <div className="flex gap-4 w-full max-w-[500px]">
                <button
                  onClick={() => setMode('lossless')}
                  className={`flex-1 py-3 px-6 rounded-lg font-bold uppercase text-sm tracking-wider transition-all ${
                    mode === 'lossless'
                      ? 'bg-[#2ecc70] text-[#0a0f12] shadow-lg shadow-[#2ecc70]/30'
                      : 'bg-[#0f172a]/60 text-slate-400 border border-[#2ecc70]/20 hover:border-[#2ecc70]/40'
                  }`}
                >
                  Lossless
                </button>
                <button
                  onClick={() => setMode('lossy')}
                  className={`flex-1 py-3 px-6 rounded-lg font-bold uppercase text-sm tracking-wider transition-all ${
                    mode === 'lossy'
                      ? 'bg-[#8b5cf6] text-white shadow-lg shadow-[#8b5cf6]/30'
                      : 'bg-[#0f172a]/60 text-slate-400 border border-[#8b5cf6]/20 hover:border-[#8b5cf6]/40'
                  }`}
                >
                  Lossy Tactical
                </button>
              </div>
            )}
          </div>

          {/* Right: Metrics */}
          <div className="lg:col-span-3 flex flex-col gap-6 h-full">
            {/* Lossless Metric */}
            <div className="p-6 rounded-2xl flex flex-col gap-4 backdrop-blur-xl bg-gradient-to-br from-[#0f172a] to-[#064e3b] border border-[#2ecc70]/20">
              <div className="flex justify-between items-start">
                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Lossless Compression</span>
                <span className="text-[#2ecc70] text-lg">✓</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold tracking-tighter text-white">70%</span>
                <span className="text-[#2ecc70] text-xs font-bold">+12.4%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-[#2ecc70] h-full w-[70%]"></div>
              </div>
            </div>

            {/* Lossy Metric */}
            <div className="p-6 rounded-2xl flex flex-col gap-4 backdrop-blur-xl bg-gradient-to-br from-[#0f172a] to-[#064e3b] border border-[#8b5cf6]/20">
              <div className="flex justify-between items-start">
                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Lossy Tactical</span>
                <span className="text-[#8b5cf6] text-lg">⚡</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold tracking-tighter text-white">90%</span>
                <span className="text-[#8b5cf6] text-xs font-bold">+8.1%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-[#8b5cf6] h-full w-[90%]"></div>
              </div>
            </div>

            {/* Processing Stats */}
            {stats && (
              <div className="mt-auto p-5 rounded-2xl backdrop-blur-xl bg-gradient-to-br from-[#0f172a] to-[#064e3b] border border-[#2ecc70]/10 flex flex-col gap-5">
                <h4 className="text-[10px] uppercase tracking-widest text-slate-400 font-bold flex items-center gap-2">
                  <span className="size-1.5 rounded-full bg-[#8b5cf6] animate-pulse"></span>
                  Processing Stats
                </h4>
                <div className="grid grid-cols-1 gap-4 font-mono">
                  {stats.format && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Format</span>
                      <span className="text-sm text-white font-bold">{stats.format}</span>
                    </div>
                  )}
                  {stats.mode && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Mode</span>
                      <span className="text-sm text-white font-bold">{stats.mode}</span>
                    </div>
                  )}
                  {stats.originalSizeKB && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Original Size</span>
                      <span className="text-sm text-slate-300">{stats.originalSizeKB} KB</span>
                    </div>
                  )}
                  {stats.compressedSizeKB && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Compressed Size</span>
                      <span className="text-sm text-[#2ecc70] font-bold italic">{stats.compressedSizeKB} KB</span>
                    </div>
                  )}
                  {stats.decompressedSizeKB && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Decompressed Size</span>
                      <span className="text-sm text-[#2ecc70] font-bold italic">{stats.decompressedSizeKB} KB</span>
                    </div>
                  )}
                  {stats.compressionRatio && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Compression Ratio</span>
                      <span className="text-sm text-[#2ecc70] font-bold">{stats.compressionRatio}%</span>
                    </div>
                  )}
                  {stats.frames && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Frames</span>
                      <span className="text-sm text-white">{stats.frames}</span>
                    </div>
                  )}
                  {stats.triangles && (
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <span className="text-[9px] text-slate-500 uppercase">Triangles</span>
                      <span className="text-sm text-white">{stats.triangles}</span>
                    </div>
                  )}
                </div>
                <div className="text-[8px] text-slate-600 text-center uppercase tracking-tighter">
                  Real-time telemetry stream optimized
                </div>
              </div>
            )}

            {error && (
              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                <p className="text-red-400 text-xs font-mono">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Dashboard Stats */}
        <div className="w-full grid grid-cols-2 md:grid-cols-4 gap-6 pt-12 border-t border-[#2ecc70]/10">
          <div className="flex flex-col gap-1">
            <span className="text-[9px] uppercase tracking-[0.2em] text-slate-500">Latency Peak</span>
            <span className="text-lg font-bold text-slate-200">0.04ms</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[9px] uppercase tracking-[0.2em] text-slate-500">Node Entropy</span>
            <span className="text-lg font-bold text-slate-200">0.002%</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[9px] uppercase tracking-[0.2em] text-slate-500">Protocol Layer</span>
            <span className="text-lg font-bold text-slate-200">L7 Quantum</span>
          </div>
          <div className="flex flex-col gap-1 text-right">
            <span className="text-[9px] uppercase tracking-[0.2em] text-slate-500">Uptime</span>
            <span className="text-lg font-bold text-[#2ecc70]">99.9999%</span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-4 px-6 lg:px-20 backdrop-blur-xl bg-[#0f172a]/60 border-t border-[#2ecc70]/10 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="size-2 rounded-full bg-[#2ecc70] animate-pulse"></div>
          <span className="text-[9px] font-mono tracking-widest text-slate-500 uppercase">
            Core Stability: Nominal // System Time: {new Date().toLocaleTimeString()}
          </span>
        </div>
        <div className="flex gap-6 text-[9px] font-mono text-slate-500 uppercase tracking-widest">
          <span>Ref: MZ-001</span>
          <span>Zone: Hive-Global-1</span>
          <span>© 2024 MedZip</span>
        </div>
      </footer>
    </div>
  );
}
