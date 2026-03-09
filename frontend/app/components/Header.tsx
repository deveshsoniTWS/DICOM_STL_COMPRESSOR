interface HeaderProps {
  view: 'compress' | 'decompress' | 'contributors';
  onViewChange: (view: 'compress' | 'decompress' | 'contributors') => void;
}

export default function Header({ view, onViewChange }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-6 lg:px-20 py-6 border-b border-[#2ecc70]/10 backdrop-blur-xl bg-[#0f172a]/60 sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="size-8 bg-gradient-to-br from-[#2ecc70] to-[#8b5cf6] flex items-center justify-center rounded-lg shadow-lg shadow-[#2ecc70]/20">
          <span className="text-[#0a0f12] text-xl font-bold">⬡</span>
        </div>
        <h2 className="text-xl font-bold tracking-tight uppercase">MedZip</h2>
      </div>
      <nav className="hidden md:flex items-center gap-10">
        <button
          onClick={() => onViewChange('compress')}
          className={`text-[11px] uppercase tracking-[0.2em] font-medium transition-colors ${
            view === 'compress' ? 'text-[#2ecc70]' : 'text-slate-400 hover:text-[#2ecc70]'
          }`}
        >
          COMPRESS
        </button>
        <button
          onClick={() => onViewChange('decompress')}
          className={`text-[11px] uppercase tracking-[0.2em] font-medium transition-colors ${
            view === 'decompress' ? 'text-[#2ecc70]' : 'text-slate-400 hover:text-[#2ecc70]'
          }`}
        >
          DECOMPRESS
        </button>
        <button
          onClick={() => onViewChange('contributors')}
          className={`text-[11px] uppercase tracking-[0.2em] font-medium transition-colors ${
            view === 'contributors' ? 'text-[#2ecc70]' : 'text-slate-400 hover:text-[#2ecc70]'
          }`}
        >
          CONTRIBUTORS
        </button>
      </nav>
      <div className="flex items-center gap-6">
        <button className="px-5 py-2 bg-[#2ecc70]/10 hover:bg-[#2ecc70]/20 border border-[#2ecc70]/30 rounded-full text-[10px] font-bold uppercase tracking-widest text-[#2ecc70] transition-all">
          BumbleBeeDev
        </button>
      </div>
    </header>
  );
}
