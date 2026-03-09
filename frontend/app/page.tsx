'use client';

import { useState } from 'react';
import Header from './components/Header';
import ProjectOverview from './components/ProjectOverview';
import UploadZone from './components/UploadZone';
import MetricsPanel from './components/MetricsPanel';
import Footer from './components/Footer';
import { compressFile, decompressFile, downloadBlob, CompressionStats, formatFileSize } from './lib/api';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<'lossless' | 'lossy'>('lossless');
  const [view, setView] = useState<'compress' | 'decompress' | 'contributors'>('compress');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<CompressionStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const operation = view === 'decompress' ? 'decompress' : 'compress';

  const handleViewChange = (newView: 'compress' | 'decompress' | 'contributors') => {
    setView(newView);
    setFile(null);
    setStats(null);
    setError(null);
  };

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    setStats(null);
    setError(null);
  };

  const handleModeChange = (newMode: 'lossless' | 'lossy') => {
    console.log('Mode changed to:', newMode);
    setMode(newMode);
  };

  const handleSubmit = async (mode: 'lossless' | 'lossy') => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setStats(null);

    try {
      if (operation === 'compress') {
        const { blob, stats: responseStats, filename } = await compressFile(file, mode);
        setStats(responseStats);
        downloadBlob(blob, filename);
      } else {
        const { blob, stats: responseStats, filename } = await decompressFile(file);
        setStats(responseStats);
        downloadBlob(blob, filename);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex flex-col overflow-x-hidden bg-[#0a0f12]">
      {/* Grid Background */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            'radial-gradient(circle at 2px 2px, rgba(46, 204, 112, 0.05) 1px, transparent 0)',
          backgroundSize: '40px 40px',
        }}
      ></div>

      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-[#2ecc70]/10 rounded-full blur-[120px]"></div>
        <div className="absolute top-1/2 -right-24 w-[500px] h-[500px] bg-[#8b5cf6]/10 rounded-full blur-[150px]"></div>
      </div>

      <Header view={view} onViewChange={handleViewChange} />

      <main className="flex-1 flex flex-col items-center justify-center px-6 lg:px-20 py-12 gap-12 max-w-7xl mx-auto w-full">
        {view === 'contributors' ? (
          // Contributors View
          <div className="w-full">
            <div className="text-center mb-16">
              <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">Contributors</h1>
              <p className="text-slate-400 text-lg">The team behind MedZip</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 w-full max-w-5xl mx-auto">
              {[
                { name: 'Devesh Soni', image: '/contributors/Devesh.png' },
                { name: 'Kavish Vijay', image: '/contributors/Kavish.png' },
                { name: 'Mansha Sharma', image: '/contributors/Mansha.png' },
              ].map((contributor, index) => (
                <div
                  key={index}
                  className="flex flex-col items-center gap-6 p-8 rounded-2xl backdrop-blur-xl bg-[#0f172a]/60 border border-[#2ecc70]/20 hover:border-[#2ecc70]/60 transition-all hover:scale-105"
                >
                  <div className="w-48 h-48 rounded-full bg-gradient-to-br from-[#2ecc70]/20 to-[#8b5cf6]/20 flex items-center justify-center border-4 border-[#2ecc70]/30 overflow-hidden">
                    <img
                      src={contributor.image}
                      alt={contributor.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        e.currentTarget.parentElement!.innerHTML = `<span class="text-6xl text-[#2ecc70]">👤</span>`;
                      }}
                    />
                  </div>
                  <h3 className="text-2xl font-bold text-white tracking-tight">{contributor.name}</h3>
                </div>
              ))}
            </div>
          </div>
        ) : (
          // Compress/Decompress View
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start w-full">
          <ProjectOverview />
          <UploadZone
            operation={operation}
            mode={mode}
            file={file}
            loading={loading}
            onFileChange={handleFileChange}
            onModeChange={handleModeChange}
            onSubmit={() => handleSubmit(mode)}
          />
          <MetricsPanel 
            stats={stats} 
            error={error} 
            operation={operation}
            mode={mode}
            onModeSelect={handleModeChange}
          />
        </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
