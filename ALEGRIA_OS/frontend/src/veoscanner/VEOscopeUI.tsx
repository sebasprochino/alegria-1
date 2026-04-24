import React, { useState, useRef } from 'react';
import { Eye, Upload, Zap, Search, Database, ArrowRight, CheckCircle2, Layout, MessageSquare, Target, Info } from 'lucide-react';
import ColorSwatch from '../components/ColorSwatch';

interface VEOscopeProps {
  onBack?: () => void;
  activeBrandId?: string;
}

export default function VEOscopeUI({ onBack, activeBrandId = "AlegrIA" }: VEOscopeProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const categories = [
    { id: 'marca', label: 'MARCA', icon: <Zap size={18} /> },
    { id: 'persona', label: 'PERSONA', icon: <Info size={18} /> },
    { id: 'producto', label: 'PRODUCTO', icon: <Layout size={18} /> },
    { id: 'idea', label: 'IDEA', icon: <Eye size={18} /> },
    { id: 'artista', label: 'ARTISTA', icon: <MessageSquare size={18} /> },
    { id: 'medios', label: 'MEDIOS', icon: <Eye size={18} /> },
    { id: 'servicios', label: 'SERVICIOS', icon: <Database size={18} /> },
    { id: 'eventos', label: 'EVENTOS', icon: <Target size={18} /> },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResults(null);
      setSaved(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setSaved(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('message', "Analiza marca e identidad visual");

      const res = await fetch('/api/veoscope/analyze-upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (data.status === 'ok' || data.status === 'success' || data.content) {
        // El backend puede devolver el resultado en content, analysis o raw_text
        let parsedResults = data.content || data.analysis || data.raw_text;
        if (typeof parsedResults === 'string') {
          try {
            // Limpiar Markdown si lo hay
            const jsonStr = parsedResults.replace(/```json/g, '').replace(/```/g, '').trim();
            parsedResults = JSON.parse(jsonStr);
          } catch (e) {
            console.error("Error parseando resultados de VEOscope:", e);
            parsedResults = {}; // Fallback para no dejar colgado el UI
          }
        }
        setResults(parsedResults);
      }
    } catch (err) {
      console.error("Error en análisis VEO:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveToBrand = async () => {
    if (!results || !preview) return;
    
    try {
      // Convertir preview (blob) a base64 para el guardado
      const blob = await fetch(preview).then(r => r.blob());
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = async () => {
        const base64data = reader.result;

        const res = await fetch('/api/veoscope/save-to-brand', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: base64data,
            analysis: results,
            brand_id: activeBrandId
          }),
        });

        const data = await res.json();
        if (data.status === 'success') {
          setSaved(true);
        }
      };
    } catch (err) {
      console.error("Error guardando en Brand Studio:", err);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#EEF2F7] h-full overflow-hidden animate-fade-in custom-scrollbar overflow-y-auto p-6 lg:p-10 font-sans">
      
      {/* HEADER TÉCNICO */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
           <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
              <Eye className="text-white" size={24} />
           </div>
           <div>
              <h1 className="text-2xl font-bold text-slate-800 tracking-tighter">VEOSCOPE ENGINE</h1>
              <p className="text-[10px] text-slate-400 font-mono uppercase tracking-[0.2em]">Clinical Observation & Visual DNA Extraction</p>
           </div>
        </div>
        <div className="flex gap-2">
           <button onClick={onBack} className="btn-operative-primary">Terminal</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-7xl mx-auto w-full">
        
        {/* INTERFACE IZQUIERDA: CAPTURA [VEOSCOPE_ENGINE_INTERFACE] */}
        <div className="lg:col-span-5 space-y-6">
           <div className="operative-card p-6 min-h-[400px] flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">[VEOSCOPE_ENGINE_INTERFACE]</span>
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                  <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                </div>
              </div>

              <div 
                onClick={() => fileInputRef.current?.click()}
                className={`flex-1 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-all cursor-pointer relative overflow-hidden ${
                  preview ? 'border-transparent bg-slate-50' : 'border-slate-200 hover:border-indigo-400 hover:bg-slate-50'
                }`}
              >
                 {preview ? (
                   <>
                    <img src={preview} alt="Visual Reference" className="absolute inset-0 w-full h-full object-contain p-4" />
                    <div className="absolute inset-0 bg-slate-900/10 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                       <Upload className="text-white" size={32} />
                    </div>
                   </>
                 ) : (
                   <div className="text-center">
                      <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4 text-slate-400">
                         <Upload size={24} />
                      </div>
                      <p className="text-sm font-bold text-slate-600">SUBIR IMAGEN PARA ANALIZAR</p>
                      <p className="text-[10px] text-slate-400 font-mono mt-1">[ADN_AUDIOVISUAL_SOURCE]</p>
                   </div>
                 )}
              </div>
              
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*" title="Seleccionar imagen para analizar" />

              <button 
                onClick={handleAnalyze}
                disabled={!file || isAnalyzing}
                className={`mt-6 w-full py-4 rounded-xl flex items-center justify-center gap-2 font-bold text-xs uppercase tracking-widest transition-all ${
                  isAnalyzing ? 'bg-slate-100 text-slate-400 cursor-wait' : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-100'
                }`}
              >
                {isAnalyzing ? (
                   <>
                    <div className="w-4 h-4 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                    Analizando DNA...
                   </>
                ) : (
                   <>
                    <Search size={16} />
                    Iniciar Análisis Clínico
                   </>
                )}
              </button>
           </div>
        </div>

        {/* INTERFACE DERECHA: RESULTADOS [TECHNICAL ANALYSIS MODULES] */}
        <div className="lg:col-span-7 space-y-6">
           
           {!results && !isAnalyzing && (
              <div className="h-full flex flex-col items-center justify-center p-12 text-center opacity-40">
                 <div className="w-20 h-20 border-2 border-slate-200 rounded-full flex items-center justify-center mb-6">
                    <Database size={32} className="text-slate-300" />
                 </div>
                 <h3 className="text-slate-400 font-mono uppercase tracking-widest text-xs">Esperando Ingesta de Datos</h3>
                 <p className="text-[10px] text-slate-400 mt-2 max-w-[240px]">Cargue una referencia visual para iniciar la disección de identidad.</p>
              </div>
           )}

           {isAnalyzing && (
             <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="operative-card p-6 h-32 animate-pulse bg-white/50"></div>
                ))}
             </div>
           )}

           {results && (
             <div className="space-y-6 animate-slide-in">
                
                {/* ADN VISUAL */}
                <div className="operative-card p-6 border-l-4 border-l-indigo-500">
                   <div className="flex items-center gap-2 mb-4">
                      <Layout size={14} className="text-indigo-500" />
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">[ADN_VISUAL]</span>
                   </div>
                   <div className="grid grid-cols-2 gap-4">
                      <div>
                         <label className="text-[9px] text-slate-400 uppercase font-bold">Composición</label>
                         <p className="text-xs text-slate-700 font-medium">{results.adn_visual?.composicion || "Analizando..."}</p>
                      </div>
                      <div>
                         <label className="text-[9px] text-slate-400 uppercase font-bold">Estilo</label>
                         <p className="text-xs text-slate-700 font-medium">{results.adn_visual?.estilo || "Analizando..."}</p>
                      </div>
                   </div>
                   <div className="mt-4">
                      <label className="text-[9px] text-slate-400 uppercase font-bold">Paleta Detectada</label>
                      <div className="flex gap-2 mt-1">
                         {results.adn_visual?.colores?.map((c: string, idx: number) => (
                           <ColorSwatch key={idx} color={c} className="w-6 h-6 rounded-md shadow-sm border border-slate-100" />
                         ))}
                      </div>
                   </div>
                </div>

                {/* CONTEXTO NARRATIVO */}
                <div className="operative-card p-6 border-l-4 border-l-teal-500">
                   <div className="flex items-center gap-2 mb-4">
                      <MessageSquare size={14} className="text-teal-500" />
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">[CONTEXTO_NARRATIVO]</span>
                   </div>
                   <div>
                      <label className="text-[9px] text-slate-400 uppercase font-bold">Voz y Mood</label>
                      <p className="text-xs text-slate-700 leading-relaxed italic">
                        "{results.contexto_narrativo?.voz || results.contexto_narrativo?.historia}"
                      </p>
                      <p className="text-[11px] text-slate-500 mt-2 font-medium">Mood: {results.contexto_narrativo?.mood || results.contexto_narrativo?.emocion}</p>
                   </div>
                </div>

                {/* SUGERENCIA DE MARCA */}
                <div className="operative-card p-6 border-l-4 border-l-amber-500">
                   <div className="flex items-center gap-2 mb-4">
                      <Target size={14} className="text-amber-500" />
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">[SUGERENCIA_DE_MARCA]</span>
                   </div>
                   <ul className="space-y-2">
                      {results.sugerencias_marca?.map((s: string, idx: number) => (
                        <li key={idx} className="text-xs text-slate-600 flex items-start gap-2">
                           <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></div>
                           {s}
                        </li>
                      ))}
                   </ul>
                </div>

                {/* CATEGORIZACIÓN SOBERANA */}
                <div className="operative-card p-8 bg-white shadow-xl shadow-slate-200/50">
                   <div className="flex items-center justify-between mb-8">
                      <div>
                         <h3 className="text-lg font-bold text-slate-800 tracking-tight">Categorización Soberana</h3>
                         <p className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">Select output vector for injection</p>
                      </div>
                      <div className="w-10 h-10 bg-slate-50 rounded-full flex items-center justify-center text-slate-300">
                         <Layout size={20} />
                      </div>
                   </div>

                   <div className="grid grid-cols-2 gap-4">
                      {categories.map((cat) => (
                         <button
                           key={cat.id}
                           onClick={() => setSelectedCategory(cat.id)}
                           className={`group relative flex items-center gap-4 p-5 rounded-[24px] transition-all duration-300 border-2 ${
                             selectedCategory === cat.id 
                               ? 'bg-indigo-600 border-indigo-600 shadow-xl shadow-indigo-200 translate-y-[-2px]' 
                               : 'bg-transparent border-transparent hover:bg-slate-50 text-slate-400'
                           }`}
                         >
                            <div className={`transition-colors duration-300 ${
                              selectedCategory === cat.id ? 'text-white' : 'text-slate-300 group-hover:text-indigo-400'
                            }`}>
                               {cat.icon}
                            </div>
                            <span className={`text-[11px] font-black tracking-[0.1em] transition-colors duration-300 ${
                              selectedCategory === cat.id ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'
                            }`}>
                               {cat.label}
                            </span>
                            {selectedCategory === cat.id && (
                              <div className="absolute right-6 w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                            )}
                         </button>
                      ))}
                   </div>
                </div>

                {/* ACCIÓN DE INYECCIÓN */}
                <div className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <Database className="text-indigo-600" size={20} />
                      <div>
                         <p className="text-xs font-bold text-indigo-900">¿Inyectar en Brand Studio?</p>
                         <p className="text-[10px] text-indigo-500">Sincroniza el ADN visual con la galería persistente.</p>
                      </div>
                   </div>
                   <button 
                     onClick={handleSaveToBrand}
                     disabled={saved || !selectedCategory}
                     className={`px-6 py-2 rounded-xl text-[11px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all ${
                       saved ? 'bg-green-500 text-white cursor-default' : 
                       !selectedCategory ? 'bg-slate-200 text-slate-400 cursor-not-allowed' :
                       'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md shadow-indigo-100'
                     }`}
                   >
                     {saved ? (
                       <><CheckCircle2 size={14} /> Sincronizado</>
                     ) : (
                       <><ArrowRight size={14} /> Inyectar Ahora</>
                     )}
                   </button>
                </div>

             </div>
           )}

        </div>
      </div>

      {/* FOOTER CLÍNICO */}
      <div className="mt-12 max-w-7xl mx-auto w-full border-t border-slate-200 pt-6">
         <div className="flex items-start gap-4 text-slate-400">
            <Info size={16} className="shrink-0 mt-1" />
            <p className="text-[11px] leading-relaxed max-w-3xl">
              El ojo clínico de ALEGR-IA. Analiza profundamente el ADN audiovisual, interpreta la narrativa y genera configuraciones de marca integrales sin intervención humana repetitiva. El sistema sugiere, el operador decide y construye.
            </p>
         </div>
      </div>

    </div>
  );
}
