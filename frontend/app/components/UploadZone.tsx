'use client';

import React from 'react';

interface UploadZoneProps {
  operation: 'compress' | 'decompress';
  mode: 'lossless' | 'lossy';
  file: File | null;
  loading: boolean;
  onFileChange: (file: File | null) => void;
  onModeChange: (mode: 'lossless' | 'lossy') => void;
  onSubmit: () => void;
}

export default function UploadZone({
  operation,
  mode,
  file,
  loading,
  onFileChange,
  onModeChange,
  onSubmit,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = React.useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      onFileChange(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set to false if leaving the main container
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      onFileChange(selectedFile);
    }
  };

  const handleModeClick = (newMode: 'lossless' | 'lossy') => {
    console.log('Mode button clicked:', newMode);
    onModeChange(newMode);
  };

  return (
    <div className="lg:col-span-6 flex flex-col items-center gap-8">
      <div className="w-full aspect-square max-w-[500px] relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-[#2ecc70] via-[#8b5cf6] to-[#2ecc70] rounded-3xl opacity-20 group-hover:opacity-40 blur transition-opacity duration-500"></div>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          className="relative w-full h-full backdrop-blur-xl bg-[#0f172a]/60 border border-[#2ecc70]/10 rounded-3xl border-2 border-dashed border-[#2ecc70]/30 flex flex-col items-center justify-center p-12 overflow-hidden"
        >
          {/* Drag overlay */}
          {isDragging && (
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-20 flex items-center justify-center pointer-events-none">
              <div className="text-4xl font-bold text-slate-400 uppercase tracking-wider">
                Drop Here
              </div>
            </div>
          )}
          {/* Hexagon Pattern */}
          <div
            className="absolute inset-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage: `linear-gradient(30deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                linear-gradient(150deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                linear-gradient(30deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                linear-gradient(150deg, #2ecc70 12%, transparent 12.5%, transparent 87%, #2ecc70 87.5%, #2ecc70),
                linear-gradient(60deg, #2ecc70 25%, transparent 25.5%, transparent 75%, #2ecc70 75%, #2ecc70),
                linear-gradient(60deg, #2ecc70 25%, transparent 25.5%, transparent 75%, #2ecc70 75%, #2ecc70)`,
              backgroundSize: '80px 140px',
            }}
          ></div>

          <div className="z-10 flex flex-col items-center text-center gap-6">
            <div className="size-24 rounded-full bg-[#2ecc70]/20 flex items-center justify-center ring-8 ring-[#2ecc70]/5 group-hover:scale-110 transition-transform duration-500">
              <span className="text-[#2ecc70] text-5xl">📁</span>
            </div>
            <div>
              <h3 className="text-2xl font-bold tracking-tight text-white mb-2">
                {operation === 'compress' ? 'UPLOAD' : 'Decompress Archive'}
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
              onChange={handleFileInput}
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
                onClick={onSubmit}
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
    </div>
  );
}
