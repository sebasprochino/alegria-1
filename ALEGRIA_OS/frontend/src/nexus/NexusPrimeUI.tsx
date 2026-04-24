import React, { useState, useEffect } from 'react';
import { 
  Zap, CreditCard, Search, ChevronDown, 
  ArrowLeft, Cpu, Database, FileText, Share2, X, Terminal, Target
} from 'lucide-react';

interface NexusPrimeUIProps {
  onBack: () => void;
}

export default function NexusPrimeUI({ onBack }: NexusPrimeUIProps) {
  const [activeBrand, setActiveBrand] = useState<any>(null);
  const [assetType, setAssetType] = useState('Fuente NotebookLM');
  const [isGenerating, setIsGenerating] = useState(false);
  const [cardSource, setCardSource] = useState('');

  useEffect(() => {
    fetchActiveBrand();
  }, []);

  const fetchActiveBrand = async () => {
    try {
      const res = await fetch('/api/brand/active');
      const data = await res.json();
      setActiveBrand(data);
    } catch (e) {
      console.error("Error fetching brand for Nexus:", e);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#EEF2F7] min-h-full overflow-hidden animate-fade-in font-sans tracking-tight custom-scrollbar overflow-y-auto pb-20">
      
      {/* HEADER OPERATIVO */}
      <div className="p-4 flex items-center justify-between bg-white border-b border-slate-200 z-10 shadow-sm">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack} 
            aria-label="Regresar al panel principal"
            title="Regresar"
            className="p-2 hover:bg-slate-100 rounded-full transition-all text-slate-400"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="text-left">
            <h2 className="text-sm font-bold tracking-[0.2em] uppercase text-slate-800 font-premium">
              NEXUS PRIME // Motor de Identidad Digital & Social Hunting
            </h2>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
            <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">Sincronización Activa</span>
          </div>
        </div>
      </div>

      <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto w-full">
        
        {/* PANEL IZQUIERDO: Taller & Social */}
        <div className="space-y-8">
            
            {/* Taller de Tarjetas Digitales */}
            <div className="operative-card p-8">
               <h3 className="text-sm font-bold text-slate-700 mb-6 flex items-center gap-2 uppercase tracking-widest">
                 Taller de Tarjetas Digitales
               </h3>
               
               <div className="flex gap-2">
                 <input 
                   placeholder="Pegá tu sitio web, instagram o escribí tu profesión..."
                   className="flex-1 bg-white border border-slate-200 rounded-xl px-6 py-4 text-xs text-slate-600 outline-none focus:border-indigo-300 transition-all font-mono shadow-inner"
                   value={cardSource}
                   onChange={(e) => setCardSource(e.target.value)}
                 />
                 <button className="bg-[#A29BFE] hover:bg-[#8C7AE6] text-white px-6 py-4 rounded-xl font-bold text-[10px] uppercase tracking-widest transition-all shadow-lg shadow-indigo-200">
                   Generar Tarjeta
                 </button>
               </div>
            </div>

            {/* Explorador de Rubro & Mercado */}
            <div className="operative-card p-8">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                     <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block">Usar Marca Activa</label>
                     <div className="flex items-center gap-3">
                        <button className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-[10px] font-bold text-slate-600 hover:bg-slate-100 transition-all uppercase tracking-widest">
                          Cargar Proyecto
                        </button>
                        <div className="flex items-center gap-2 px-4 py-3 bg-slate-50 rounded-xl border border-slate-100">
                           <div className="w-1.5 h-1.5 rounded-full bg-slate-400"></div>
                           <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{activeBrand?.name || 'Sin Proyecto'}</span>
                        </div>
                     </div>
                  </div>

                  <div className="space-y-4">
                     <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block">Explorar Rubro</label>
                     <div className="relative">
                        <input 
                          placeholder="Ej: Abogado"
                          className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 pl-10 text-[11px] text-slate-600 outline-none focus:border-indigo-300 transition-all font-mono"
                        />
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-300" size={14} />
                        <button 
                          aria-label="Buscar rubro"
                          title="Buscar"
                          className="absolute right-2 top-2 bottom-2 px-2 bg-slate-500/10 text-slate-500 rounded-lg transition-colors hover:bg-slate-500/20"
                        >
                           <Search size={12} />
                        </button>
                     </div>
                  </div>
               </div>
            </div>
        </div>

        {/* PANEL DERECHO: Ingeniería de Prompts */}
        <div className="space-y-8">
            <div className="operative-card p-8 flex flex-col h-full bg-white/80">
               <div className="space-y-10 flex-1">
                  <div className="space-y-4">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block">Tipo de Activo a Generar</label>
                    <div className="relative">
                       <select 
                         aria-label="Seleccionar tipo de activo"
                         title="Tipo de Activo"
                         className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-xl px-6 py-4 text-xs font-bold text-slate-700 outline-none focus:ring-4 focus:ring-indigo-500/5 transition-all cursor-pointer uppercase tracking-widest"
                         value={assetType}
                         onChange={(e) => setAssetType(e.target.value)}
                       >
                         <option>Fuente NotebookLM</option>
                         <option>Video Tutorial</option>
                         <option>Entrevista Podcast</option>
                         <option>Social Hunting Feed</option>
                       </select>
                       <ChevronDown className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
                    </div>
                  </div>

                  <div className="bg-slate-50/50 border border-slate-100 rounded-3xl p-8 space-y-6">
                    <div className="flex items-center gap-3">
                       <Zap size={14} className="text-indigo-500" />
                       <span className="text-[10px] font-bold text-slate-700 uppercase tracking-[0.2em]">Ejecutar Ingeniería de Prompts</span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed font-mono">Referenciando prompts: <strong>{activeBrand?.name || 'NotebookLM'}</strong>.</p>
                    
                    <button 
                      className={`w-full py-5 rounded-xl flex items-center justify-center gap-3 transition-all font-bold text-[10px] uppercase tracking-[0.2em] shadow-xl ${
                        isGenerating 
                        ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
                        : 'bg-[#6A9AB1] hover:bg-[#5A8AA1] text-white shadow-slate-200'
                      }`}
                    >
                      Generar Configuración
                    </button>
                  </div>
               </div>

               <div className="mt-8 pt-8 border-t border-slate-100 flex items-center justify-between opacity-50">
                  <div className="flex items-center gap-2">
                     <Target size={14} className="text-indigo-500" />
                     <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Nexus Prime Status: Ready</span>
                  </div>
                  <div className="flex gap-4 text-slate-400">
                     <Share2 size={16} className="hover:text-indigo-600 cursor-pointer transition-colors" />
                     <Database size={16} className="hover:text-indigo-600 cursor-pointer transition-colors" />
                  </div>
               </div>
            </div>
        </div>

      </div>

      {/* FOOTER TÉCNICO */}
      <div className="max-w-7xl mx-auto w-full px-8 pt-4">
        <div className="bg-white/40 border border-slate-200 rounded-[32px] p-8 text-center">
          <p className="text-[12px] text-slate-500 font-mono leading-relaxed max-w-4xl mx-auto">
            No es un simple buscador. Es ingeniería de prompts automatizada que escanea repositorios, sintetiza investigación en guiones de podcast, e inyecta contexto en modelos externos como NotebookLM.
          </p>
          <div className="mt-4 flex items-center justify-center gap-2 opacity-20 grayscale">
             <img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/Google_NotebookLM_logo.png" alt="NotebookLM" className="h-4" />
             <span className="text-[8px] font-bold tracking-[0.4em] uppercase">NotebookLM Integration</span>
          </div>
        </div>
      </div>

    </div>
  );
}
