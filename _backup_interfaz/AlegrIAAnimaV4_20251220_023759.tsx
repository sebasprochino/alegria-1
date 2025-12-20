import React, { useState, useCallback } from 'react';
import { 
  Zap, LayoutDashboard, MessageSquare, Radio, 
  Search, Play, Square, AlertCircle, Wind, Flower2 
} from 'lucide-react';

// --- LÓGICA DE VOZ GRATUITA (Anima Chordata) ---
const useAnimaVoice = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const speak = useCallback((text: string) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-ES';
    utterance.rate = 0.85; // Tono calmado y profesional (Directora Ejecutiva)
    utterance.pitch = 1.0;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, []);
  return { speak, isSpeaking, stop: () => window.speechSynthesis.cancel() };
};

export default function AlegrIAAnimaV4() {
  const [activeTab, setActiveTab] = useState('genesis');
  const { speak, isSpeaking, stop } = useAnimaVoice();
  const [seed, setSeed] = useState('');

  // Filosofía Constitucional: Modo de Contingencia y Relax
  const haiku = "Luz que no abandona,\nsi el camino se fractura,\nla idea respira.";
  const relaxPhrase = "Cierra los ojos. Tu visión está segura conmigo. Respira, la coherencia volverá a fluir.";

  return (
    <div className="flex h-screen bg-[#F5F6F7] text-[#23262C] font-sans">
      {/* SIDEBAR CON MÓDULOS v4.0 */}
      <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col shadow-sm">
        <div className="flex items-center gap-2 mb-8 px-2">
          <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-bold font-serif italic text-xl">A</div>
          <span className="font-bold text-lg tracking-tight">AlegrIA Anima</span>
        </div>

        <nav className="space-y-1 flex-1">
          <button onClick={() => setActiveTab('dash')} className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'dash' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-500 hover:bg-gray-50'}`}>
            <LayoutDashboard size={18}/> <span className="text-sm font-semibold">Dashboard</span>
          </button>
          <button onClick={() => setActiveTab('genesis')} className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'genesis' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-500 hover:bg-gray-50'}`}>
            <Zap size={18}/> <span className="text-sm font-semibold">Génesis</span>
          </button>
          <button onClick={() => setActiveTab('contingencia')} className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'contingencia' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-500 hover:bg-gray-50'}`}>
            <AlertCircle size={18}/> <span className="text-sm font-semibold">Contingencia</span>
          </button>
          <button onClick={() => setActiveTab('relax')} className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${activeTab === 'relax' ? 'bg-purple-600 text-white shadow-lg' : 'text-gray-500 hover:bg-blue-50 hover:text-blue-500'}`}>
            <Wind size={18}/> <span className="text-sm font-semibold">Santuario Zen</span>
          </button>
        </nav>
      </aside>

      {/* ÁREA DE TRABAJO DINÁMICA */}
      <main className="flex-1 p-8 flex flex-col relative overflow-hidden">
        
        {/* MÓDULO GÉNESIS */}
        {activeTab === 'genesis' && (
          <div className="max-w-3xl mx-auto w-full space-y-8 animate-in fade-in slide-in-from-bottom-4">
            <header className="text-center space-y-2">
              <h2 className="text-4xl font-serif">¿Cuál es la Semilla hoy?</h2>
              <p className="text-gray-500 text-sm tracking-wide">Anima Chordata depurará tu idea con Nexus y Radar.</p>
            </header>
            <div className="bg-white p-8 rounded-[40px] border border-gray-100 shadow-sm space-y-6">
              <textarea 
                className="w-full h-40 p-5 bg-gray-50 rounded-3xl border-none focus:ring-2 focus:ring-purple-200 text-lg transition-all"
                placeholder="Describe tu idea semilla..."
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
              />
              <div className="flex justify-between items-center">
                <button onClick={() => isSpeaking ? stop() : speak(seed || "Anima espera tu idea")} className="flex items-center gap-2 text-purple-600 font-bold text-xs uppercase tracking-widest">
                  {isSpeaking ? <Square size={16}/> : <Play size={16}/>} {isSpeaking ? 'Detener' : 'Escuchar Anima'}
                </button>
                <button onClick={() => speak("Ritual de Refinamiento iniciado")} className="bg-purple-600 text-white px-10 py-4 rounded-2xl font-bold shadow-xl hover:bg-purple-700 transition-all active:scale-95">
                  ⚡ MATERIALIZAR
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODO CONTINGENCIA (Haiku Poético) */}
        {activeTab === 'contingencia' && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 animate-in zoom-in duration-500">
            <div className="bg-white p-12 rounded-[50px] border border-purple-50 shadow-sm relative">
              <p className="font-serif text-2xl italic text-gray-700 leading-relaxed whitespace-pre-line mb-8">{haiku}</p>
              <button onClick={() => speak(haiku)} className="bg-purple-600 text-white px-8 py-3 rounded-2xl font-bold flex items-center gap-2 mx-auto hover:bg-purple-700">
                 <Play size={16}/> RECITAR ESPERANZA
              </button>
            </div>
            <p className="text-xs text-gray-400 uppercase tracking-widest">Ley de la Esperanza Activa</p>
          </div>
        )}

        {/* MODO RELAX (Santuario Zen) */}
        {activeTab === 'relax' && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-8 animate-in fade-in duration-1000">
            <div className="relative">
              <div className="absolute inset-0 animate-ping bg-blue-100 rounded-full scale-150 opacity-20"></div>
              <Flower2 className="text-blue-400 relative" size={80} />
            </div>
            <h2 className="text-3xl font-serif text-blue-900">Santuario Zen</h2>
            <p className="text-gray-500 italic max-w-md">"{relaxPhrase}"</p>
            <button onClick={() => speak(relaxPhrase)} className="bg-blue-500 text-white px-10 py-4 rounded-full font-bold shadow-lg shadow-blue-100 hover:bg-blue-600 transition-all">
              {isSpeaking ? 'SINTIENDO...' : 'INICIAR RITUAL DE CALMA'}
            </button>
          </div>
        )}

      </main>
    </div>
  );
}
