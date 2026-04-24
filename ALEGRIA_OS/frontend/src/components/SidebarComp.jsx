import React, { useState, useEffect } from 'react';
import { Menu, Cpu, Wifi, WifiOff } from 'lucide-react';
import { categories } from './sidebarCategories';

const SidebarComp = ({ selectedChat, setSelectedChat, isSidebarOpen, setIsSidebarOpen, provider, setProvider, onOpenTools }) => {
  const [ollamaOnline, setOllamaOnline] = useState(false);

  // Ping Ollama status every 15s
  useEffect(() => {
    const checkOllama = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);
      try {
        const res = await fetch('http://localhost:11434/api/tags', { signal: controller.signal });
        setOllamaOnline(res.ok);
      } catch {
        setOllamaOnline(false);
      } finally {
        clearTimeout(timeoutId);
      }
    };
    checkOllama();
    const interval = setInterval(checkOllama, 15000);
    return () => clearInterval(interval);
  }, []);

  const isLocalMode = provider === 'ollama';

  return (
    <div
      className={`fixed md:relative z-50 flex flex-col bg-[#1E293B] h-full transition-all duration-300 border-r border-white/5 ${
        isSidebarOpen ? 'w-full md:w-64 translate-x-0' : 'w-0 md:w-20 -translate-x-full md:translate-x-0'
      }`}
    >
      <div className="relative z-10 flex flex-col h-full">

        {/* Header */}
        <div className="p-6 flex items-center justify-between border-b border-white/5">
          <div className="flex flex-col">
            <h1 className="text-base md:text-sm font-bold text-white tracking-[0.2em] font-premium uppercase">ALEGR-IA</h1>
            <span className="text-[11px] md:text-[9px] text-blue-400 font-bold uppercase tracking-[0.25em] opacity-80">OPERATIVE INTEL v5.0</span>
          </div>
          <button
            className="p-2 text-slate-400 hover:text-white transition-transform active:scale-90"
            onClick={onOpenTools}
            aria-label="Abrir herramientas"
            title="Herramientas"
          >
            <Menu size={20} />
          </button>
        </div>

        {/* Nav items */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
          {categories.map(cat => (
            <div key={cat.title}>
              <h4 className="text-[11px] md:text-[9px] font-bold text-slate-600 px-3 mb-3 tracking-[0.3em] uppercase">
                {cat.title}
              </h4>
              <div className="space-y-0.5">
                {cat.items.map(chat => (
                  <div
                    key={chat.id}
                    onClick={() => {
                      setSelectedChat(chat);
                      if (window.innerWidth < 768) setIsSidebarOpen(false);
                    }}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                      selectedChat?.id === chat.id
                        ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-lg shadow-blue-500/5'
                        : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex-shrink-0 opacity-80">{chat.icon}</div>
                    <span className="text-[14px] md:text-[12px] font-medium tracking-tight truncate">{chat.name}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer: Modo Local + Ollama Status */}
        <div className="p-4 border-t border-white/5 bg-black/20 space-y-2">

          {/* Modo Local switch */}
          <div
            onClick={() => setProvider(isLocalMode ? 'cascada' : 'ollama')}
            className={`flex items-center justify-between px-3 py-2.5 rounded-2xl border transition-all cursor-pointer ${
              isLocalMode
                ? 'bg-teal-500/10 border-teal-500/20'
                : 'bg-indigo-500/10 border-indigo-500/20'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <div className={`p-1.5 rounded-lg transition-colors ${isLocalMode ? 'bg-teal-500/20 text-teal-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
                <Cpu size={14} />
              </div>
              <div className="flex flex-col">
                <span className="text-[12px] md:text-[10px] font-bold text-slate-200 uppercase tracking-tighter">Modo Local</span>
                <span className="text-[10px] md:text-[8px] text-slate-500 font-mono">{isLocalMode ? 'ON — Soberanía Activa' : 'OFF — Cascada Cloud'}</span>
              </div>
            </div>
            {/* Toggle pill */}
            <div className={`w-8 h-4 rounded-full relative transition-colors ${isLocalMode ? 'bg-teal-500/80' : 'bg-slate-600'}`}>
              <div className={`absolute top-1 w-2 h-2 bg-white rounded-full transition-all ${isLocalMode ? 'right-1' : 'left-1'}`} />
            </div>
          </div>

          {/* Ollama status (read-only) */}
          <div className={`flex items-center gap-2.5 px-3 py-2 rounded-xl border transition-all ${
            ollamaOnline ? 'bg-emerald-500/5 border-emerald-500/15' : 'bg-red-500/5 border-red-500/15'
          }`}>
            <div className={`p-1.5 rounded-lg ${ollamaOnline ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'}`}>
              {ollamaOnline ? <Wifi size={13} /> : <WifiOff size={13} />}
            </div>
            <div className="flex flex-col flex-1">
              <span className="text-[12px] md:text-[10px] font-bold text-slate-300 uppercase tracking-tighter">Ollama</span>
              <span className={`text-[10px] md:text-[8px] font-mono font-bold ${ollamaOnline ? 'text-emerald-400' : 'text-red-400'}`}>
                {ollamaOnline ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className={`w-1.5 h-1.5 rounded-full ${ollamaOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
          </div>

        </div>
      </div>
    </div>
  );
};

export default SidebarComp;
