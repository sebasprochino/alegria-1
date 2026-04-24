import React from 'react';
import { Database, Folder, FileJson, Search, Clock } from 'lucide-react';

const MemoryCard = ({ title, type, date, size }) => (
  <div className="bg-[#111b21] border border-[#222d34] p-4 rounded-lg hover:bg-[#202c33] transition-colors cursor-pointer group">
    <div className="flex items-start justify-between mb-3">
      <div className={`p-2 rounded-lg ${type === 'core' ? 'bg-purple-900/30 text-purple-400' : 'bg-blue-900/30 text-blue-400'}`}>
        {type === 'core' ? <Database size={18} /> : <FileJson size={18} />}
      </div>
      <span className="text-[#8696a0] text-xs">{date}</span>
    </div>
    <h3 className="text-[#e9edef] font-medium mb-1 group-hover:text-[#00a884] transition-colors">{title}</h3>
    <p className="text-[#8696a0] text-xs">{size} • {type === 'core' ? 'Memoria Fundacional' : 'Registro de Sesión'}</p>
  </div>
);

const NexusView = ({ update = () => console.log("update nexus") }) => {
  return (
    <div className="flex flex-col h-full bg-[#0b141a]">
      {/* Header */}
      <header className="h-[60px] bg-[#111b21] px-6 flex items-center justify-between border-b border-[#222d34]">
        <h2 className="text-xl font-light text-[#e9edef] flex items-center gap-2">
          <Database className="text-[#00a884]" size={20} />
          Nexus Memory System
        </h2>
        <div className="flex gap-2">
           <div className="bg-[#202c33] rounded-lg px-3 py-1.5 flex items-center gap-2 text-[#8696a0] focus-within:text-[#e9edef] w-64">
             <Search size={16} />
             <input type="text" placeholder="Buscar en recuerdos..." className="bg-transparent border-none outline-none text-sm w-full" />
           </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mb-6 bg-[#111b21] border border-[#222d34] p-4 rounded-lg">
          <h3 className="text-[#8696a0] text-sm uppercase tracking-wider mb-3 font-medium">Presets de Estado (Nexus)</h3>
          <button
            onClick={() => update({
              no_explanations: true,
              max_length: 60,
              mode: "analysis"
            })}
            className="w-full bg-zinc-800 hover:bg-zinc-700 transition-colors p-2 rounded text-xs text-slate-200"
          >
            modo rigor
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MemoryCard title="Identidad_Base.json" type="core" date="Hoy, 10:00" size="12 KB" />
          <MemoryCard title="Sesión_29_12_2025" type="session" date="Hace 2 horas" size="45 KB" />
          <MemoryCard title="Proyecto_ALEGRIA_Context" type="session" date="Ayer" size="128 KB" />
          <MemoryCard title="Manifiesto_Soberania.md" type="core" date="23/12/2025" size="8 KB" />
        </div>
        
        <div className="mt-8 border-t border-[#222d34] pt-6">
           <h3 className="text-[#8696a0] text-sm uppercase tracking-wider mb-4 font-medium">Estadísticas de Memoria</h3>
           <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-[#202c33] p-4 rounded-lg">
                <span className="text-[#8696a0] text-xs block mb-1">Total Recuerdos</span>
                <span className="text-2xl text-[#e9edef]">1,240</span>
             </div>
             <div className="bg-[#202c33] p-4 rounded-lg">
                <span className="text-[#8696a0] text-xs block mb-1">Uso de Disco</span>
                <span className="text-2xl text-[#e9edef]">45 MB</span>
             </div>
              <div className="bg-[#202c33] p-4 rounded-lg">
                <span className="text-[#8696a0] text-xs block mb-1">Última Sincronización</span>
                <span className="text-xl text-[#e9edef]">Hace 5m</span>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default NexusView;