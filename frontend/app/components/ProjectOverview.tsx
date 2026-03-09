export default function ProjectOverview() {
  return (
    <div className="lg:col-span-3 flex flex-col gap-8 pt-12">
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <span className="h-px w-8 bg-[#2ecc70]"></span>
          <span className="text-[10px] uppercase tracking-[0.3em] text-[#2ecc70] font-bold">
            Project Overview
          </span>
        </div>
        <p className="text-sm leading-relaxed text-slate-300 font-light border-l border-[#2ecc70]/20 pl-4">
          <span className="text-[#2ecc70] font-bold">MedZip</span> is designed to simplify the handling of large DICOM and STL files. 
          The platform provides an easy way to compress and decompress files while maintaining important data and visual quality.
        </p>
        <div className="flex items-center gap-2 pt-4 opacity-50">
          <span className="h-px w-4 bg-[#8b5cf6]"></span>
          <span className="text-[9px] uppercase tracking-[0.2em] text-[#8b5cf6] font-mono italic">
            End of Summary
          </span>
        </div>
      </div>
    </div>
  );
}
