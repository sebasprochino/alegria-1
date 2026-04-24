import React, { useState } from 'react';
import { Bot, Search, Loader2, CheckCircle2, AlertCircle, Sparkles, Terminal, Box } from 'lucide-react';

export default function AppAgentUI() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleInvestigate = () => {
    if (!query.trim()) return;
    setIsSearching(true);
    setTimeout(() => setIsSearching(false), 2000);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] h-full overflow-hidden">
      {/* Header */}
      <div className="px-8 pt-12 pb-8 text-center">
        <div className="flex items-center justify-center gap-4 mb-3">
          <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20 shadow-lg shadow-blue-500/5">
            <Bot size={28} className="text-blue-400" />
          </div>
          <div className="text-left">
            <h1 className="text-3xl font-black text-white tracking-tight">App Agent</h1>
            <p className="text-slate-500 text-sm font-medium">
              Genera instaladores con detección de puertos
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-start pt-10 px-6">
        <div className="w-full max-w-3xl space-y-6">
          
          {/* Status Bar */}
          <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl px-4 py-3 flex items-center gap-3">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <p className="text-[11px] text-emerald-500/80 font-mono tracking-tight">
              Sistema <span className="font-bold">AutoCascade</span> activo (Ollama Cloud · Fireworks · Groq · Gemini · Local)
            </p>
          </div>

          {/* Input Box */}
          <div className="bg-[#161b22] border border-white/[0.08] rounded-[32px] p-8 shadow-2xl space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] text-slate-500 uppercase tracking-widest font-black ml-1">Describe la aplicación</label>
              <div className="flex gap-3">
                <div className="flex-1 relative group">
                  <input 
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleInvestigate()}
                    placeholder="ej: Dashboard, E-commerce, Landing..."
                    className="w-full bg-[#0d1117] border border-white/[0.08] rounded-2xl px-6 py-4 text-[15px] text-white placeholder-slate-600 outline-none focus:border-blue-500/40 transition-all font-light"
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-focus-within:opacity-100 transition-opacity">
                    <Sparkles size={16} className="text-blue-500/50" />
                  </div>
                </div>
                <button 
                  onClick={handleInvestigate}
                  disabled={isSearching}
                  className={`px-8 rounded-2xl flex items-center gap-2 text-[12px] font-black uppercase tracking-widest transition-all ${
                    isSearching 
                      ? 'bg-slate-800 text-slate-600 cursor-wait' 
                      : 'bg-[#1c2330] border border-white/10 text-slate-300 hover:bg-white/5 hover:text-white active:scale-95'
                  }`}
                >
                  {isSearching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                  Investigar
                </button>
              </div>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
            {[
              { icon: <Terminal size={16} />, title: 'Terminal Automático', desc: 'Detección y configuración de puertos.' },
              { icon: <Box size={16} />, title: 'Instalador One-Click', desc: 'Paquetización de dependencias.' },
              { icon: <Sparkles size={16} />, title: 'Optimización AI', desc: 'Refactorización de código en vuelo.' },
            ].map((feature, i) => (
              <div key={i} className="bg-white/[0.02] border border-white/[0.05] rounded-2xl p-4 space-y-2 hover:bg-white/[0.04] transition-colors group">
                <div className="w-8 h-8 rounded-lg bg-blue-500/5 flex items-center justify-center text-blue-400 group-hover:bg-blue-400 group-hover:text-white transition-all">
                  {feature.icon}
                </div>
                <h4 className="text-[12px] font-bold text-white tracking-tight">{feature.title}</h4>
                <p className="text-[10px] text-slate-500 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}
