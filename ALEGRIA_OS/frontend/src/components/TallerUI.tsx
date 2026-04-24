import React, { useState } from 'react';
import { Search, MoreHorizontal, Send, Mic, Paperclip, ChevronRight, Sparkles, Database, Globe, Code2, FileCode, Newspaper, Palette, Shield, Video } from 'lucide-react';

interface TallerItem {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const SECTIONS = [
  {
    title: 'Proyectos Activos',
    items: [
      { id: 'anima', name: 'Anima - Visual Effects', description: 'Finalizar trayectos anima - visual effects', icon: <Palette size={18} />, color: 'bg-purple-500' },
      { id: 'nexus', name: 'Nexus - Red IA', description: 'Ajustar conexión con proyectos para IA', icon: <Database size={18} />, color: 'bg-blue-500' },
      { id: 'veoscanner', name: 'Veoscanner - Análisis de Marca', description: 'Escaneo de análisis de marca de IA', icon: <Video size={18} />, color: 'bg-pink-500' },
    ]
  },
  {
    title: 'Investigación en Curso',
    items: [
      { id: 'radar', name: 'Radar - Nichos Emergentes', description: 'Emergentes en nichos emergentes en IA', icon: <Globe size={18} />, color: 'bg-emerald-500' },
      { id: 'competencia', name: 'Análisis de Competencia', description: 'Comparar sistemas de competencia', icon: <Shield size={18} />, color: 'bg-slate-500' },
    ]
  },
  {
    title: 'Herramientas y Recursos',
    items: [
      { id: 'developer', name: 'Developer - React Native/Flutter', description: 'Developer - Roast Native/Flutter', icon: <Code2 size={18} />, color: 'bg-sky-500' },
      { id: 'snippets', name: 'Snippets - Código', description: 'Código crear mis snippets', icon: <FileCode size={18} />, color: 'bg-amber-500' },
      { id: 'news', name: 'News - Novedades IA', description: 'Novedades relevantes en IA', icon: <Newspaper size={18} />, color: 'bg-indigo-500' },
    ]
  }
];

export default function TallerUI() {
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState('');

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden font-sans relative">
      {/* Background Pattern (Subtle dots or mesh) */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />

      {/* Header */}
      <div className="bg-[#1f2c34] px-6 pt-12 pb-4 flex flex-col gap-4 shadow-lg z-10">
        <div className="flex items-center justify-between">
          <button className="text-white hover:opacity-70 transition-opacity">
            <ChevronRight size={24} className="rotate-180" />
          </button>
          <h1 className="text-white font-bold text-lg">Taller</h1>
          <button className="text-white hover:opacity-70 transition-opacity">
            <MoreHorizontal size={24} />
          </button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input 
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar"
            className="w-full bg-[#111b21] border-none rounded-xl pl-12 pr-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:ring-1 focus:ring-emerald-500/30 transition-all"
          />
        </div>
      </div>

      {/* Content List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-1 py-4 space-y-8 z-10">
        <div className="max-w-md mx-auto space-y-8">
          {SECTIONS.map((section) => (
            <div key={section.title} className="space-y-3">
              <h3 className="px-5 text-sm font-bold text-white tracking-tight">{section.title}</h3>
              <div className="space-y-0.5">
                {section.items.map((item) => (
                  <div 
                    key={item.id}
                    className="flex items-center gap-4 px-5 py-3 hover:bg-[#1f2c34] transition-colors cursor-pointer group"
                  >
                    <div className={`w-12 h-12 ${item.color} rounded-2xl flex items-center justify-center text-white shadow-lg group-hover:scale-105 transition-transform`}>
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0 border-b border-white/5 pb-3">
                      <div className="flex justify-between items-center mb-0.5">
                        <h4 className="text-[15px] font-bold text-white truncate">{item.name}</h4>
                        <span className="text-[10px] text-slate-500 font-medium">Ahora</span>
                      </div>
                      <p className="text-[13px] text-slate-500 truncate font-medium">
                        {item.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile Input (WhatsApp style) */}
      <div className="p-4 bg-[#1f2c34] flex items-center gap-3 z-20">
        <button className="text-slate-400 hover:text-white transition-colors">
          <Paperclip size={22} className="rotate-45" />
        </button>
        <div className="flex-1 bg-[#2a3942] rounded-2xl px-4 py-3 flex items-center gap-3 border border-white/5 shadow-inner">
           <input 
             type="text"
             value={message}
             onChange={(e) => setMessage(e.target.value)}
             placeholder="Mensaje"
             className="flex-1 bg-transparent border-none text-[15px] text-white placeholder-slate-500 outline-none"
           />
           <button className="text-slate-500 hover:text-slate-300">
             <Mic size={20} />
           </button>
        </div>
        <button className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 transition-colors shrink-0">
          <Send size={20} className="ml-1" />
        </button>
      </div>
    </div>
  );
}
