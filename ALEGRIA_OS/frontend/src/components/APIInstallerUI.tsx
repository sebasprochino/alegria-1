import React, { useState } from 'react';
import { Package, Search, ChevronRight, Loader2, Sparkles, Terminal, Cpu, Database, Zap } from 'lucide-react';

export default function APIInstallerUI() {
  const [search, setSearch] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedApi, setSelectedApi] = useState<string | null>(null);

  const handleSearch = () => {
    if (!search.trim()) return;
    setIsSearching(true);
    setTimeout(() => setIsSearching(false), 1500);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] h-full overflow-hidden">
      {/* Header */}
      <div className="px-10 pt-12 pb-8 border-b border-white/5">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-purple-500/10 rounded-2xl flex items-center justify-center border border-purple-500/20">
            <Package size={20} className="text-purple-400" />
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">API Installer Engine</h1>
        </div>
        <p className="text-slate-500 text-[13px] font-medium">
          Busca, selecciona y genera integraciones completas automáticamente.
        </p>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Search */}
        <div className="w-96 border-r border-white/5 p-8 space-y-6 overflow-y-auto custom-scrollbar">
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input 
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Buscar APIs (ej: weather, crypto, animals)"
                className="w-full bg-[#161b22] border border-white/[0.1] rounded-xl pl-12 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none focus:border-purple-500/40 transition-all"
              />
            </div>
            <button 
              onClick={handleSearch}
              disabled={isSearching}
              className="w-full bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-600 text-white py-3 rounded-xl text-[12px] font-black uppercase tracking-widest transition-all shadow-lg shadow-purple-600/20 flex items-center justify-center gap-2"
            >
              {isSearching ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
              Buscar
            </button>
          </div>

          <div className="space-y-3">
             <p className="text-[10px] text-slate-500 uppercase tracking-widest font-black ml-1">Resultados Populares</p>
             {[
               { id: '1', name: 'OpenWeather Map', category: 'Weather', icon: <Zap size={14} /> },
               { id: '2', name: 'CoinGecko API', category: 'Finance', icon: <Database size={14} /> },
               { id: '3', name: 'Giphy SDK', category: 'Media', icon: <Sparkles size={14} /> },
             ].map(api => (
               <div 
                key={api.id}
                onClick={() => setSelectedApi(api.name)}
                className={`flex items-center justify-between p-4 rounded-2xl border cursor-pointer transition-all ${
                  selectedApi === api.name 
                    ? 'bg-purple-500/10 border-purple-500/30' 
                    : 'bg-white/[0.02] border-white/[0.05] hover:bg-white/[0.05]'
                }`}
               >
                 <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-slate-400">
                      {api.icon}
                    </div>
                    <div>
                      <h4 className="text-[12px] font-bold text-white">{api.name}</h4>
                      <p className="text-[10px] text-slate-500">{api.category}</p>
                    </div>
                 </div>
                 <ChevronRight size={14} className="text-slate-600" />
               </div>
             ))}
          </div>
        </div>

        {/* Right Panel: Selected / Empty State */}
        <div className="flex-1 bg-[#090e14] flex flex-col items-center justify-center p-12 text-center">
          {!selectedApi ? (
            <div className="space-y-6 max-w-sm">
              <div className="w-20 h-20 bg-white/5 rounded-[28px] border border-white/10 flex items-center justify-center mx-auto shadow-inner">
                <ChevronRight size={32} className="text-slate-700 animate-pulse" />
              </div>
              <div className="space-y-2">
                <h3 className="text-white text-lg font-bold">Selecciona una API para comenzar</h3>
                <p className="text-slate-500 text-sm leading-relaxed">
                  Busca en nuestro catálogo o selecciona uno de los resultados populares para ver los detalles técnicos y generar el instalador.
                </p>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-2xl space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 text-left">
               <div className="flex items-center gap-6">
                  <div className="w-16 h-16 bg-purple-500/10 rounded-2xl border border-purple-500/20 flex items-center justify-center text-purple-400">
                     <Package size={32} />
                  </div>
                  <div>
                    <h2 className="text-3xl font-black text-white">{selectedApi}</h2>
                    <p className="text-emerald-400 text-xs font-mono font-bold uppercase tracking-widest mt-1">Status: Ready to Install</p>
                  </div>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-[#161b22] border border-white/5 rounded-2xl p-6 space-y-4">
                     <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        <Terminal size={16} className="text-purple-400" />
                        CLI Auto-Generation
                     </h4>
                     <p className="text-xs text-slate-400 leading-relaxed">
                        Generaremos el código de conexión y las dependencias necesarias automáticamente.
                     </p>
                     <button className="w-full bg-white/5 border border-white/10 hover:bg-white/10 text-white py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                        Preview Code
                     </button>
                  </div>
                  <div className="bg-[#161b22] border border-white/5 rounded-2xl p-6 space-y-4">
                     <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        <Cpu size={16} className="text-emerald-400" />
                        Logic Integration
                     </h4>
                     <p className="text-xs text-slate-400 leading-relaxed">
                        Se inyectará la lógica de negocio directamente en tu motor operativo ALEGR-IA.
                     </p>
                     <button className="w-full bg-emerald-500 text-white py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all shadow-lg shadow-emerald-500/20">
                        Install Engine
                     </button>
                  </div>
               </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
