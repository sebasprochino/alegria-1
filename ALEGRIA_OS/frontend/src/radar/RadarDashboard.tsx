import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Search, Newspaper, Globe, Mic, FileText, Bookmark, 
  Zap, Upload, Terminal, Sparkles, TrendingUp, Cpu, Hash, 
  Loader2, RefreshCw, BarChart3, Radio, ShieldCheck
} from 'lucide-react';

interface Props {
  onBack: () => void;
}

interface Trend {
  id: string;
  topic: string;
  relevance: number;
  source: string;
}

const RadarDashboard: React.FC<Props> = ({ onBack }) => {
  const [query, setQuery] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState<string | null>(null);
  const [trends] = useState<Trend[]>([
    { id: '1', topic: 'LLMs Multimodales SOBERANOS', relevance: 98, source: 'Internal Scan' },
    { id: '2', topic: 'Tokenización de Activos Reales (RWA)', relevance: 85, source: 'Twitter Trends' },
    { id: '3', topic: 'Gemini 3.0 Leak Analysis', relevance: 92, source: 'Reddit AI' },
  ]);

  const handleScan = React.useCallback(async () => {
    if (!query.trim()) return;
    setExtracting(true);
    setReport(null);
    setProgress(0);
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return prev;
        return prev + 5;
      });
    }, 400);

    try {
      const response = await fetch('/api/radar/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      if (data.status === 'ok') {
        setProgress(100);
        setReport(data.report);
      }
    } catch (e) {
      console.error("Radar error:", e);
    } finally {
      clearInterval(interval);
      setExtracting(false);
    }
  }, [query]);

  const handleDiscover = React.useCallback(async () => {
    setExtracting(true);
    try {
      const res = await fetch('/api/radar/discover');
      const data = await res.json();
      if (data.findings) {
        setReport(`### Descubrimientos de Radar\n\n${JSON.stringify(data.findings, null, 2)}`);
      }
    } catch (e) {
       console.error("Discover error:", e);
    } finally {
      setExtracting(false);
    }
  }, []);

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] text-slate-100 h-full overflow-hidden animate-fade-in font-sans tracking-tight">
      
      {/* HEADER TÉCNICO */}
      <div className="p-5 flex items-center justify-between bg-[#111b21] border-b border-white/5 z-20 shadow-xl">
        <div className="flex items-center gap-5">
          <button 
            onClick={onBack} 
            className="p-3 hover:bg-white/5 rounded-2xl transition-all text-slate-500 hover:text-white"
            title="Regresar"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="flex flex-col">
            <h2 className="text-[11px] font-black tracking-[0.3em] uppercase text-purple-400">
              SISTEMA RADAR // v4.2
            </h2>
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
               <span className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Escaneo de Nivel S5 Activo</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
           <button 
             onClick={handleDiscover}
             className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 text-[10px] font-bold uppercase tracking-widest transition-all"
           >
             <Cpu size={14} className="text-purple-400" />
             Descubrir Modelos
           </button>
           <div className="w-px h-6 bg-white/10" />
           <div className="flex items-center gap-2 text-slate-500">
             <Radio size={16} className="animate-pulse text-emerald-500" />
             <span className="text-[10px] font-mono">127.0.0.1 // PROBE_CONNECTED</span>
           </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 lg:p-10 space-y-10 custom-scrollbar">
        
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10">
          
          {/* LADO IZQUIERDO: TENDENCIAS Y ESTADÍSTICAS */}
          <div className="lg:col-span-4 space-y-8">
            <div className="operative-card p-6 bg-[#162129] border-white/5">
               <div className="flex items-center justify-between mb-6">
                 <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                   <TrendingUp size={14} className="text-emerald-500" />
                   Tendencias Detectadas
                 </h3>
                 <RefreshCw size={12} className="text-slate-600 cursor-pointer hover:rotate-180 transition-transform duration-500" />
               </div>
               
               <div className="space-y-4">
                 {trends.map(trend => (
                   <div key={trend.id} className="p-4 bg-[#0b141a] rounded-2xl border border-white/5 hover:border-purple-500/30 transition-all cursor-pointer group">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-[13px] font-bold text-white group-hover:text-purple-400 transition-colors">{trend.topic}</span>
                        <span className="text-[10px] font-bold text-emerald-500">{trend.relevance}%</span>
                      </div>
                      <div className="flex items-center gap-2">
                         <Hash size={10} className="text-slate-600" />
                         <span className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">{trend.source}</span>
                      </div>
                   </div>
                 ))}
               </div>
               
               <button className="w-full mt-6 py-3 border border-dashed border-white/10 rounded-xl text-[10px] font-bold text-slate-500 uppercase tracking-widest hover:border-purple-500/30 hover:text-purple-400 transition-all">
                 Ver Mapa Completo
               </button>
            </div>

            <div className="operative-card p-6 bg-gradient-to-br from-purple-600/10 to-indigo-600/10 border-purple-500/20">
               <h3 className="text-[10px] font-black text-purple-400 uppercase tracking-[0.2em] mb-4">Sensores de Mercado</h3>
               <div className="flex items-end gap-2 h-24 pt-4">
                 {[40, 70, 45, 90, 65, 80, 50, 85].map((h, i) => (
                   <div 
                     key={i} 
                     className="flex-1 bg-purple-500/30 rounded-t-sm animate-fade-in-up" 
                     style={{ height: `${h}%`, animationDelay: `${i * 0.1}s` }} 
                   />
                 ))}
               </div>
               <p className="text-[9px] text-slate-500 mt-4 leading-relaxed font-mono">
                 Carga cognitiva global aumentando un 12% en el sector de automatización creativa.
               </p>
            </div>
          </div>

          {/* LADO DERECHO: TERMINAL Y REPORTES */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* TERMINAL DE INVESTIGACIÓN */}
            <div className="operative-card p-8 bg-[#162129] border-white/5 relative overflow-hidden group">
               <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
                 <Radio size={80} className="text-purple-500" />
               </div>
               
               <div className="relative z-10 space-y-6">
                 <div className="flex items-center gap-3 mb-2">
                   <div className="w-8 h-8 rounded-xl bg-purple-600/20 flex items-center justify-center border border-purple-500/30">
                     <Terminal size={16} className="text-purple-400" />
                   </div>
                   <span className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Mandato de Investigación</span>
                 </div>

                 <div className="relative">
                   <input 
                    className="w-full bg-[#0b141a] border border-white/5 rounded-2xl py-6 pl-14 pr-8 text-white placeholder-slate-700 outline-none focus:ring-2 focus:ring-purple-500/30 transition-all font-mono text-base"
                    placeholder="Escribe el tema, URL o keyword para el escaneo..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleScan()}
                  />
                  <div className="absolute left-6 top-1/2 -translate-y-1/2 text-purple-500 font-mono">{'>'}</div>
                 </div>
                 
                 <div className="flex items-center gap-3">
                   <button
                    onClick={handleScan}
                    disabled={extracting || !query.trim()}
                    className="flex-1 py-4 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-30 transition-all flex items-center justify-center gap-4 font-black text-white text-[10px] uppercase tracking-[0.2em] shadow-2xl shadow-purple-600/20"
                  >
                    {extracting ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} />}
                    {extracting ? 'Escaneando Ecosistema...' : 'Lanzar Sonda de Radar'}
                  </button>
                  <button className="p-4 bg-white/5 rounded-2xl border border-white/5 text-slate-500 hover:text-white transition-all">
                    <Mic size={20} />
                  </button>
                 </div>
               </div>
            </div>

            {/* BARRA DE PROGRESO (Solo si escanea) */}
            {extracting && (
              <div className="space-y-2 animate-fade-in">
                <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                   <span>Sincronizando flujos de datos...</span>
                   <span>{progress}%</span>
                </div>
                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                   <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                   />
                </div>
              </div>
            )}

            {/* RESULTADOS / REPORTE */}
            {report && (
              <div className="operative-card bg-[#162129] border-white/5 overflow-hidden animate-fade-in-up">
                <div className="flex justify-between items-center px-8 py-5 border-b border-white/5 bg-white/[0.02]">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-purple-500" />
                    <span className="text-[10px] font-black text-white uppercase tracking-widest">Síntesis Operativa</span>
                  </div>
                  <div className="flex gap-4">
                    <button className="text-[9px] font-bold text-slate-500 uppercase hover:text-white flex items-center gap-1.5">
                      <Bookmark size={12} /> Guardar
                    </button>
                    <button className="text-[9px] font-bold text-purple-400 uppercase hover:text-purple-300 flex items-center gap-1.5">
                      <Upload size={12} /> Exportar a Nexus
                    </button>
                  </div>
                </div>
                
                <div className="p-8">
                  <pre className="text-[13px] text-slate-200 font-mono whitespace-pre-wrap leading-relaxed selection:bg-purple-500/30 max-h-[500px] overflow-y-auto custom-scrollbar">
                    {report}
                  </pre>
                </div>
              </div>
            )}

            {!report && !extracting && (
               <div className="flex flex-col items-center justify-center py-20 text-center space-y-6 opacity-30">
                  <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                    <BarChart3 size={40} className="text-slate-600" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-sm font-bold uppercase tracking-widest">Bandeja de Inteligencia Vacía</h4>
                    <p className="text-[10px] max-w-xs leading-relaxed">
                      Introduce un mandato para que Radar comience el escaneo de tendencias y fuentes externas.
                    </p>
                  </div>
               </div>
            )}

          </div>
        </div>
      </div>
      
      {/* FOOTER BAR */}
      <div className="px-10 py-5 border-t border-white/5 bg-black/40 flex justify-between items-center text-slate-600">
        <div className="flex items-center gap-2">
          <ShieldCheck size={12} />
          <span className="text-[9px] font-black uppercase tracking-widest">Radar Intelligence Core · Sovereign Architecture</span>
        </div>
        <div className="flex gap-4">
          <span className="text-[9px] font-bold">RADAR_PROBE: ONLINE</span>
        </div>
      </div>
    </div>
  );
};

export default RadarDashboard;
