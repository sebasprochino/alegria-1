import React, { useState } from 'react';
import { Settings, Cpu, Database, Save, Shield, Globe, Terminal, Zap } from 'lucide-react';
import ProvidersBlock from '../blocks/ProvidersBlock';

interface SettingsUIProps {
  onBack: () => void;
}

export default function SettingsUI({ onBack }: SettingsUIProps) {
  const [activeTab, setActiveTab] = useState('apis');

  const tabs = [
    { id: 'apis', name: 'APIs y Conexión', icon: <Globe size={16} /> },
    { id: 'lexico', name: 'Léxico y Voz', icon: <Terminal size={16} /> },
    { id: 'memoria', name: 'Memoria y Contexto', icon: <Database size={16} /> }
  ];

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden animate-fade-in custom-scrollbar overflow-y-auto p-4 md:p-12 relative">
      <div className="max-w-4xl mx-auto w-full">
         
         <div className="flex items-center gap-4 mb-10">
            <div className="p-3 bg-blue-600/10 rounded-2xl border border-blue-500/20 text-blue-400">
               <Settings size={24} />
            </div>
            <div>
               <h2 className="text-3xl font-display font-bold text-white tracking-tighter">
                 {activeTab === 'apis' ? 'Configuración de APIs' : activeTab === 'lexico' ? 'Léxico y Voz' : 'Memoria y Contexto'}
               </h2>
               <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
                 {activeTab === 'apis' ? 'Gestiona tus conexiones a la IA' : activeTab === 'lexico' ? 'Identidad comunicativa del sistema' : 'Gestión de contexto y persistencia'}
               </p>
            </div>
         </div>

         <div className="flex flex-col md:flex-row gap-8">
            
            {/* Sidebar de Tabs */}
            <div className="w-full md:w-64 space-y-2 flex-shrink-0">
               {tabs.map(tab => (
                  <button
                     key={tab.id}
                     onClick={() => setActiveTab(tab.id)}
                     className={`w-full flex items-center gap-3 p-4 rounded-2xl transition-all border ${
                        activeTab === tab.id ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20' : 'bg-white/5 border-transparent text-gray-400 hover:bg-white/10'
                     }`}
                  >
                     {tab.icon}
                     <span className="text-sm font-bold tracking-tight">{tab.name}</span>
                  </button>
               ))}
            </div>

            {/* Contenido Dinámico */}
            <div className="flex-1 min-w-0">
               {activeTab === 'apis' && (
                  <ProvidersBlock />
               )}

               {activeTab === 'lexico' && (
                  <div className="bg-[#1f2c34]/20 border border-white/5 rounded-3xl p-8 shadow-2xl backdrop-blur-xl space-y-6 animate-fade-in">
                     <div className="space-y-4">
                        <label className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest block font-mono">Brand Voice (Tono)</label>
                        <select 
                           aria-label="Tono de voz de la marca"
                           className="w-full bg-[#0b141a] border border-white/10 rounded-xl p-4 text-white text-sm outline-none cursor-pointer hover:border-emerald-500/30 transition-all appearance-none"
                        >
                           <option>Soberano y Técnico (Default)</option>
                           <option>Creativo y Disruptivo</option>
                           <option>Informativo y Neutro</option>
                        </select>
                     </div>
                     <div className="space-y-4">
                        <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block font-mono">Diccionarios de Rechazo</label>
                        <div className="flex flex-wrap gap-2">
                           <span className="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-[10px] text-gray-300 font-bold uppercase">Ética ACSP</span>
                           <span className="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-[10px] text-gray-300 font-bold uppercase">Privacidad</span>
                           <span className="bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-[10px] text-blue-400 font-bold uppercase cursor-pointer hover:bg-white/10">+ Añadir</span>
                        </div>
                     </div>
                  </div>
               )}

               {activeTab === 'memoria' && (
                  <div className="bg-[#1f2c34]/20 border border-white/5 rounded-3xl p-8 shadow-2xl backdrop-blur-xl space-y-6 animate-fade-in">
                     <div className="grid grid-cols-2 gap-4">
                        <div className="bg-[#0b141a] p-4 rounded-2xl border border-white/5 space-y-2">
                           <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block font-mono">Contexto Activo</span>
                           <span className="text-xl font-bold text-white tracking-tighter">8,192 Tokens</span>
                        </div>
                        <div className="bg-[#0b141a] p-4 rounded-2xl border border-white/5 space-y-2">
                           <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block font-mono">Persistencia</span>
                           <span className="text-xl font-bold text-blue-400 tracking-tighter">Nexus Sync</span>
                        </div>
                     </div>
                     <div className="pt-4 flex items-center gap-3">
                        <button className="flex-1 bg-red-500/10 border border-red-500/20 text-red-500 py-3 rounded-xl text-[10px] font-bold uppercase tracking-widest hover:bg-red-500 hover:text-white transition-all">Limpiar Memoria Local</button>
                        <button className="flex-1 bg-white/5 border border-white/10 text-gray-400 py-3 rounded-xl text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all">Descargar Log Semántico</button>
                     </div>
                  </div>
               )}
            </div>
         </div>

         <div className="mt-12 flex justify-between items-center border-t border-white/5 pt-8">
            <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">
               <Shield size={12} className="text-blue-500/50" />
               Configuración Encriptada de Fin a Fin
            </div>
            <button className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-8 py-3 rounded-2xl flex items-center gap-2 shadow-xl shadow-emerald-600/20 transition-all uppercase text-xs tracking-widest active:scale-95">
               <Save size={16} />
               Guardar Cambios
            </button>
         </div>

      </div>
    </div>
  );
}
