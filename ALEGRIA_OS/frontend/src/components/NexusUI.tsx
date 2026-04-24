import React, { useState } from 'react';
import { Shield, ThumbsDown, ThumbsUp, Plus, ExternalLink, ChevronLeft, Settings } from 'lucide-react';

interface NexusUIProps {
  onBack?: () => void;
}

export default function NexusUI({ onBack }: NexusUIProps) {
  const [element, setElement] = useState('');
  const [rejections, setRejections] = useState(['Contenido genérico', 'Falta de coherencia']);
  const [preferences, setPreferences] = useState(['Idealidad Visual Naveilo', 'Soberanía del Usuario']);

  return (
    <div className="flex-1 flex flex-col bg-black h-full overflow-hidden text-white font-sans">
      {/* Header Area */}
      <div className="px-6 pt-10 pb-6 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-2">
           <div className="w-1.5 h-6 bg-blue-500 rounded-full" />
           <span className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-500/80">Configuración Interna</span>
        </div>
        <button onClick={onBack} className="p-2 text-slate-500 hover:text-white transition-colors">
          <ChevronLeft size={20} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-8 space-y-10">
        {/* Title */}
        <h1 className="text-6xl font-black italic tracking-tighter uppercase">NEXUS</h1>

        {/* Input Block */}
        <div className="bg-[#111] border border-white/5 rounded-[32px] p-6 space-y-6">
          <input 
            type="text"
            value={element}
            onChange={(e) => setElement(e.target.value)}
            placeholder="Definir elemento..."
            className="w-full bg-transparent border-b border-white/10 py-3 text-lg outline-none focus:border-blue-500/50 transition-colors placeholder:text-slate-700"
          />
          
          <div className="flex gap-3">
            <button className="flex-1 flex items-center justify-center gap-2 py-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-500 text-[11px] font-black uppercase tracking-widest hover:bg-red-500/20 transition-all">
              <ThumbsDown size={14} />
              Rechazar
            </button>
            <button className="flex-1 flex items-center justify-center gap-2 py-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-500 text-[11px] font-black uppercase tracking-widest hover:bg-emerald-500/20 transition-all">
              <ThumbsUp size={14} />
              Preferir
            </button>
          </div>
        </div>

        {/* Rejections List */}
        <div className="space-y-4">
           <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-red-500/60">Lista de Rechazos</h3>
           <div className="flex flex-wrap gap-2">
             {rejections.map(item => (
               <div key={item} className="px-4 py-2 bg-red-500/5 border border-red-500/10 rounded-full text-[11px] font-bold text-red-400/80">
                 {item}
               </div>
             ))}
           </div>
        </div>

        {/* Preferences */}
        <div className="space-y-4">
           <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-emerald-500/60">Preferencias</h3>
           <div className="flex flex-wrap gap-2">
             {preferences.map(item => (
               <div key={item} className="px-4 py-2 bg-emerald-500/5 border border-emerald-500/10 rounded-full text-[11px] font-bold text-emerald-400/80">
                 {item}
               </div>
             ))}
           </div>
        </div>

        {/* Shortcuts */}
        <div className="space-y-4 pb-10">
           <div className="flex items-center justify-between">
              <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">Atajos Directos</h3>
              <Plus size={16} className="text-slate-700 cursor-pointer hover:text-white transition-colors" />
           </div>
           
           <div className="bg-[#111] border border-white/5 rounded-2xl p-5 flex items-center justify-between hover:bg-white/[0.03] transition-colors cursor-pointer group">
              <span className="text-[12px] font-black uppercase tracking-widest text-slate-300">Canva Pro</span>
              <ExternalLink size={14} className="text-slate-700 group-hover:text-blue-400 transition-colors" />
           </div>
        </div>

      </div>
    </div>
  );
}
