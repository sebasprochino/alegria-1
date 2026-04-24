import React from 'react';
import { Search, Zap } from 'lucide-react';

interface RadarBlockProps {
  metadata?: any;
}

const RadarBlock: React.FC<RadarBlockProps> = ({ metadata }) => {
  return (
    <div className="p-4 bg-slate-900 border border-blue-500/30 rounded-2xl shadow-lg animate-fade-in group hover:border-blue-500 transition-all">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-all">
          <Search size={20} />
        </div>
        <div>
          <h3 className="font-bold text-slate-100 uppercase tracking-tighter">Radar Scan</h3>
          <p className="text-[10px] text-slate-500 uppercase">Capacidad: Research</p>
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 animate-pulse w-[60%]" />
        </div>
        <p className="text-xs text-blue-400 font-mono">Buscando patrones en la red...</p>
      </div>
    </div>
  );
};

export default RadarBlock;
