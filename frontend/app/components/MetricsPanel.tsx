import { formatFileSize } from '../lib/api';

interface MetricsPanelProps {
  stats: any;
  error: string | null;
  operation: 'compress' | 'decompress';
  mode: 'lossless' | 'lossy';
  onModeSelect: (mode: 'lossless' | 'lossy') => void;
}

export default function MetricsPanel({ stats, error, operation, mode, onModeSelect }: MetricsPanelProps) {
  return (
    <div className="lg:col-span-3 flex flex-col gap-6 h-full">
      {/* Lossless Metric - Mode selector */}
      {operation === 'compress' && (
        <button
          onClick={() => onModeSelect('lossless')}
          className={`p-6 rounded-2xl flex flex-col gap-4 backdrop-blur-xl bg-gradient-to-br from-[#0f172a] to-[#064e3b] transition-all hover:scale-[1.02] active:scale-95 ${
            mode === 'lossless'
              ? 'border-2 border-[#2ecc70] shadow-lg shadow-[#2ecc70]/20'
              : 'border border-[#2ecc70]/30 hover:border-[#2ecc70]/60'
          }`}
        >
          <div className="flex justify-between items-start">
            <span className={`text-[10px] uppercase tracking-widest font-bold ${
              mode === 'lossless' ? 'text-[#2ecc70]' : 'text-slate-500'
            }`}>
              Lossless Compression
            </span>
            <span className="text-[#2ecc70] text-lg">{mode === 'lossless' ? '✓' : '○'}</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold tracking-tighter text-white">70%</span>
            <span className="text-[#2ecc70] text-xs font-bold">+12.4%</span>
          </div>
          <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
            <div className="bg-[#2ecc70] h-full w-[70%]"></div>
          </div>
        </button>
      )}

      {/* Lossy Metric - Mode selector */}
      {operation === 'compress' && (
        <button
          onClick={() => onModeSelect('lossy')}
          className={`p-6 rounded-2xl flex flex-col gap-4 backdrop-blur-xl bg-gradient-to-br from-[#0f172a] to-[#064e3b] transition-all hover:scale-[1.02] active:scale-95 ${
            mode === 'lossy'
              ? 'border-2 border-[#8b5cf6] shadow-lg shadow-[#8b5cf6]/20'
              : 'border border-[#8b5cf6]/30 hover:border-[#8b5cf6]/60'
          }`}
        >
          <div className="flex justify-between items-start">
            <span className={`text-[10px] uppercase tracking-widest font-bold ${
              mode === 'lossy' ? 'text-[#8b5cf6]' : 'text-slate-500'
            }`}>
              Lossy Tactical
            </span>
            <span className="text-[#8b5cf6] text-lg">{mode === 'lossy' ? '⚡' : '○'}</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold tracking-tighter text-white">90%</span>
            <span className="text-[#8b5cf6] text-xs font-bold">+8.1%</span>
          </div>
          <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
            <div className="bg-[#8b5cf6] h-full w-[90%]"></div>
          </div>
        </button>
      )}

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
                <span className="text-sm text-slate-300">{formatFileSize(stats.originalSizeKB)}</span>
              </div>
            )}
            {stats.compressedSizeKB && (
              <div className="flex justify-between items-end border-b border-white/5 pb-2">
                <span className="text-[9px] text-slate-500 uppercase">
                  {stats.decompressedSizeKB ? 'Input Size' : 'Compressed Size'}
                </span>
                <span className="text-sm text-[#2ecc70] font-bold italic">{formatFileSize(stats.compressedSizeKB)}</span>
              </div>
            )}
            {stats.decompressedSizeKB && (
              <div className="flex justify-between items-end border-b border-white/5 pb-2">
                <span className="text-[9px] text-slate-500 uppercase">Decompressed Size</span>
                <span className="text-sm text-[#2ecc70] font-bold italic">{formatFileSize(stats.decompressedSizeKB)}</span>
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

      {/* Error Display */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
          <p className="text-red-400 text-xs font-mono">{error}</p>
        </div>
      )}
    </div>
  );
}
