import React from 'react';
import { Sparkles, Activity } from 'lucide-react';

const AnimaStatusBlock = () => {
  return (
    <div className="p-4 bg-slate-900 border border-purple-500/30 rounded-2xl shadow-lg animate-fade-in group hover:border-purple-500 transition-all">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-all">
          <Sparkles size={20} />
        </div>
        <div>
          <h3 className="font-bold text-slate-100 uppercase tracking-tighter">Anima Coherence</h3>
          <p className="text-[10px] text-slate-500 uppercase">Capacidad: System Status</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <Activity size={32} className="text-purple-400 animate-pulse" />
        <div className="flex-1">
          <p className="text-2xl font-bold text-slate-100">98.4%</p>
          <p className="text-xs text-slate-500">Coherencia del Sistema</p>
        </div>
      </div>
    </div>
  );
};

export default AnimaStatusBlock;
