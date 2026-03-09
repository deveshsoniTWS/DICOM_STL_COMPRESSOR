'use client';

import { useState, useEffect } from 'react';

export default function Footer() {
  const [time, setTime] = useState('--:--:--');

  useEffect(() => {
    // Set initial time
    setTime(new Date().toLocaleTimeString());

    // Update every second
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <footer className="w-full py-4 px-6 lg:px-20 backdrop-blur-xl bg-[#0f172a]/60 border-t border-[#2ecc70]/10 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="size-2 rounded-full bg-[#2ecc70] animate-pulse"></div>
        <span className="text-[9px] font-mono tracking-widest text-slate-500 uppercase">
          Core Stability: Nominal // System Time: {time}
        </span>
      </div>
      <div className="flex gap-6 text-[9px] font-mono text-slate-500 uppercase tracking-widest">
        <span>Ref: MZ-001</span>
        <span>Zone: Hive-Global-1</span>
        <span>© 2024 MedZip</span>
      </div>
    </footer>
  );
}
