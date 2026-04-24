import React, { useState, useRef, useEffect } from 'react';
import { Search, Upload, Zap, Shield, Image as ImageIcon, Loader2, CheckCircle2, Layout, MessageSquare, Target, Info, ArrowLeft, Database, User, Package, Lightbulb, UserCircle, Tv, Briefcase, Calendar, Globe } from 'lucide-react';
import ColorSwatch from '../components/ColorSwatch';

interface BrandScannerUIProps {
  onBack: () => void;
  activeBrandId?: string;
}

const CATEGORIES = [
  { id: 'brand', name: 'Marca', icon: <Database size={14} />, color: 'bg-indigo-500' },
  { id: 'persona', name: 'Persona', icon: <User size={14} />, color: 'bg-amber-500' },
  { id: 'product', name: 'Producto', icon: <Package size={14} />, color: 'bg-teal-500' },
  { id: 'idea', name: 'Idea', icon: <Lightbulb size={14} />, color: 'bg-violet-500' },
  { id: 'artista', name: 'Artista', icon: <UserCircle size={14} />, color: 'bg-rose-500' },
  { id: 'medios', name: 'Medios', icon: <Tv size={14} />, color: 'bg-blue-500' },
  { id: 'servicios', name: 'Servicios', icon: <Briefcase size={14} />, color: 'bg-emerald-500' },
  { id: 'eventos', name: 'Eventos', icon: <Calendar size={14} />, color: 'bg-orange-500' },
];

export default function BrandScannerUI({ onBack, activeBrandId = "AlegrIA" }: BrandScannerUIProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [saved, setSaved] = useState(false);
  
  // New State for persistence control
  const [targetName, setTargetName] = useState("");
  const [targetCategory, setTargetCategory] = useState("brand");
  
  // New State for URL Scanner
  const [urlInput, setUrlInput] = useState("");
  const [isScraping, setIsScraping] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setupFile(e.target.files[0]);
    }
  };

  const setupFile = (f: File) => {
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
    setResults(null);
    setSaved(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setupFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (urlInput.trim()) {
      await handleUrlScan();
      return;
    }

    if (!file) return;
    setIsAnalyzing(true);
    setResults(null);
    setSaved(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('message', "Realiza un análisis clínico de identidad y marca para el Brand Studio.");
      
      const res = await fetch('/api/veoscope/analyze-upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      if (data.status === 'ok') {
        setResults(data.analysis || data.raw_text);
        // Default values based on analysis
        if (data.analysis?.category) setTargetCategory(data.analysis.category);
      }
    } catch (err) {
      console.error("Error en análisis Brand Scanner:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUrlScan = async () => {
    setIsScraping(true);
    setResults(null);
    setSaved(false);

    try {
      const res = await fetch('/api/brand/scan-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlInput }),
      });
      
      const data = await res.json();
      if (data.status === 'ok') {
         setTargetName(data.brand.name);
         setTargetCategory(data.brand.category);
         setResults({
            adn_visual: data.brand.gallery[0]?.analysis?.adn_visual,
            contexto_narrativo: { voz: data.brand.voice, mood: data.brand.mood },
            sugerencias_marca: ["[Soberanía Visual Extraída]", "[Perfil Inyectado al Studio]"]
         });
         setPreview(data.brand.gallery[0]?.url || "https://dummyimage.com/600x400/2a2a2a/ffffff&text=Analisis+Completado");
         setSaved(true);
      } else {
         alert("Error escaneando enlace: " + data.detail);
      }
    } catch (err) {
      console.error("Error en Crawler:", err);
      alert("Error procesando URL.");
    } finally {
      setIsScraping(false);
    }
  };

  const handleSaveToIdentity = async () => {
    if (saved) {
       onBack(); // If already auto-saved by URL flow, just go back.
       return;
    }
    if (!results || !preview) return;
    
    try {
      const blob = await fetch(preview).then(r => r.blob());
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = async () => {
        const base64data = reader.result;

        // Overlay specific user-defined context
        const finalResults = {
           ...results,
           category: targetCategory,
           name: targetName || results.name
        };

        const res = await fetch('/api/veoscope/save-to-brand', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: base64data,
            analysis: finalResults,
            brand_id: targetName || activeBrandId
          }),
        });

        const data = await res.json();
        if (data.status === 'success') {
          setSaved(true);
        }
      };
    } catch (err) {
      console.error("Error guardando en Identity Studio:", err);
    }
  };

  const activeCategory = CATEGORIES.find(c => c.id === (results?.category || targetCategory)) || CATEGORIES[0];

  return (
    <div className="flex-1 flex flex-col bg-[#EEF2F7] h-full overflow-hidden wa-background animate-fade-in relative p-6 lg:p-12 overflow-y-auto custom-scrollbar">
      
      {/* HEADER NAVEGABLE */}
      <div className="max-w-6xl mx-auto w-full mb-12 flex items-center justify-between">
        <button onClick={onBack} className="flex items-center gap-2 text-slate-400 hover:text-slate-800 transition-colors group">
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-xs font-bold uppercase tracking-widest">Regresar</span>
        </button>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
            <Search size={22} />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tighter uppercase">Brand Scanner</h2>
        </div>
        <div className="flex items-center gap-3 bg-white/50 px-4 py-2 rounded-full border border-slate-200">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Visión Soberana v5.0</span>
        </div>
      </div>

      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12">
         
         {/* SECCIÓN DE CARGA */}
         <div className="lg:col-span-5 space-y-6">
            <div className="operative-card p-8 flex flex-col items-center justify-center gap-8 min-h-[500px]">
               <input 
                 type="file" 
                 accept="image/*" 
                 className="hidden" 
                 ref={fileInputRef} 
                 onChange={handleFileChange} 
                 title="Cargar"
               />

               <div className="w-full">
                 <div className="flex items-center gap-3 w-full bg-white border-2 border-indigo-100 rounded-2xl p-2 shadow-sm focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all">
                   <div className="bg-indigo-50 text-indigo-500 p-3 rounded-xl"><Globe size={20} /></div>
                   <input 
                     type="text" 
                     placeholder="Ingresar End-Point o URL (Ej. Instagram, Web)..."
                     className="bg-transparent border-none outline-none text-sm font-bold text-slate-700 w-full placeholder:font-medium placeholder:text-slate-300"
                     value={urlInput}
                     onChange={(e) => {
                        setUrlInput(e.target.value);
                        if (e.target.value.length > 0) {
                           setFile(null);
                           setPreview(null);
                        }
                     }}
                   />
                 </div>
                 
                 <div className="flex items-center gap-4 my-6">
                    <div className="flex-1 h-px bg-slate-200"></div>
                    <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">o subir archivo físico</span>
                    <div className="flex-1 h-px bg-slate-200"></div>
                 </div>
               </div>

               <div 
                 onClick={() => fileInputRef.current?.click()}
                 onDragOver={handleDragOver}
                 onDragLeave={handleDragLeave}
                 onDrop={handleDrop}
                 className={`w-full aspect-square border-2 border-dashed rounded-[32px] flex flex-col items-center justify-center gap-6 group cursor-pointer transition-all overflow-hidden relative ${
                   isDragging ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-200 bg-slate-50 hover:border-indigo-400 hover:bg-slate-100'
                 }`}
               >
                  {preview ? (
                     <img src={preview} alt="Preview" className="absolute inset-0 w-full h-full object-contain p-4 transition-transform group-hover:scale-105" />
                  ) : (
                    <div className="text-center">
                      <div className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center mx-auto mb-6 text-slate-300 shadow-sm border border-slate-100 group-hover:text-indigo-500 transition-colors">
                         <Upload size={32} />
                      </div>
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Suelta aquí una referencia visual</p>
                      <p className="text-[9px] text-slate-300 font-mono mt-2">[IDEN_SOURCE_INGESTA]</p>
                    </div>
                  )}
               </div>

               <button 
                  onClick={handleAnalyze}
                  disabled={(!file && !urlInput.trim()) || isAnalyzing || isScraping}
                  className={`w-full py-5 rounded-2xl text-white font-bold text-sm flex items-center justify-center gap-3 shadow-xl transition-all uppercase tracking-[0.2em] ${
                    isAnalyzing || isScraping ? 'bg-slate-200 text-slate-400 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-100 active:scale-[0.98]'
                  }`}
               >
                  {isAnalyzing || isScraping ? <Loader2 size={18} className="animate-spin" /> : <Zap size={18} />}
                  {isScraping ? 'Escaneando URL & Renderizando...' : isAnalyzing ? 'Leyendo ADN...' : ((file || urlInput) ? 'Diseccionar Identidad' : 'Esperando Input')}
               </button>
            </div>
         </div>

         {/* SECCIÓN DE RESULTADOS */}
         <div className="lg:col-span-7">
            {!results && !isAnalyzing && (
               <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-white/40 border-2 border-dashed border-slate-200 rounded-[48px]">
                  <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-6 text-slate-200 border border-slate-100 shadow-sm">
                    <Database size={24} />
                  </div>
                  <h3 className="text-slate-400 text-sm font-bold uppercase tracking-[0.2em]">Ojo Clínico en Espera</h3>
                  <p className="text-[11px] text-slate-400 mt-2 max-w-xs font-medium leading-relaxed">Analiza profundamente el ADN audiovisual para extraer la esencia de marcas, personas o ideas.</p>
               </div>
            )}

            {isAnalyzing && (
               <div className="space-y-6">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-44 bg-white/60 border border-slate-200 rounded-[32px] animate-pulse"></div>
                  ))}
               </div>
            )}

            {results && (
               <div className="animate-slide-in space-y-6 pb-12">
                  
                  {/* MODULO: ANALISIS VISUAL */}
                  <div className={`p-8 rounded-[40px] border border-slate-200/60 bg-white relative overflow-hidden shadow-sm border-l-8 ${activeCategory.color.replace('bg-', 'border-')}`}>
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg text-white ${activeCategory.color}`}>
                           {activeCategory.icon}
                        </div>
                        <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest font-mono">
                          [{activeCategory.id.toUpperCase()}_CLINICAL_EYE]
                        </span>
                      </div>
                      <span className="px-3 py-1 bg-slate-50 text-[10px] font-black text-slate-500 rounded-full border border-slate-100 uppercase tracking-tight">
                        v{Math.random().toFixed(1)} Accuracy
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <label className="text-[10px] text-slate-400 uppercase font-black mb-2 block tracking-tight">Análisis Estructural</label>
                        <p className="text-sm text-slate-800 font-bold leading-relaxed font-premium">
                          {results.adn_visual?.fisonomia || results.adn_visual?.composicion}
                        </p>
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-400 uppercase font-black mb-2 block tracking-tight">Estilo & Semántica</label>
                        <p className="text-sm text-slate-800 font-bold leading-relaxed font-premium">
                          {results.adn_visual?.vestuario || results.adn_visual?.estilo}
                        </p>
                      </div>
                    </div>

                    {results.adn_visual?.colores && (
                      <div className="mt-8 pt-6 border-t border-slate-100">
                        <label className="text-[10px] text-slate-400 uppercase font-black mb-3 block tracking-tight">Paleta Cromática Identificada</label>
                        <div className="flex gap-3">
                          {results.adn_visual.colores.map((c: string, i: number) => (
                            <ColorSwatch key={i} color={c} className="w-10 h-10 rounded-2xl shadow-sm border border-slate-200/50" />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* MODULO: NARRATIVA */}
                  <div className="p-8 rounded-[40px] border border-slate-200/60 bg-white border-l-8 border-l-slate-800 shadow-sm">
                    <div className="flex items-center gap-2 mb-6">
                      <MessageSquare size={16} className="text-slate-800" />
                      <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest font-mono">[NARRATIVE_CONTEXT]</span>
                    </div>
                    <p className="text-sm text-slate-700 leading-relaxed italic font-medium border-l-4 border-slate-100 pl-6 py-2 bg-slate-50/50 rounded-r-2xl">
                      "{results.contexto_narrativo?.arquetipo || results.contexto_narrativo?.voz || results.contexto_narrativo?.historia}"
                    </p>
                  </div>

                  {/* MODULO: PERSISTENCIA SOBERANA */}
                  <div className="p-8 bg-indigo-50/50 rounded-[48px] border-2 border-indigo-100/50 shadow-inner">
                     <div className="flex items-center gap-4 mb-8">
                        <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-200">
                          <Database className="text-white" size={24} />
                        </div>
                        <div>
                          <h3 className="text-sm font-black text-indigo-900 uppercase">Inyectar en Identity Studio</h3>
                          <p className="text-[10px] text-indigo-400 font-bold tracking-widest uppercase">Persistencia y Evolución de Activos</p>
                        </div>
                     </div>

                     <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <div>
                           <label className="text-[10px] font-black text-indigo-400 uppercase mb-2 block">Nombre de la Identidad</label>
                           <input 
                             value={targetName}
                             onChange={(e) => setTargetName(e.target.value)}
                             placeholder="Ej. Artista_01, Proyecto_X..."
                             className="w-full bg-white border border-indigo-100 rounded-2xl px-5 py-4 text-sm font-bold text-indigo-900 outline-none focus:ring-4 focus:ring-indigo-200/20 transition-all shadow-sm"
                           />
                        </div>
                        <div>
                           <label className="text-[10px] font-black text-indigo-400 uppercase mb-2 block">Módulo de Categoría</label>
                           <select 
                             value={targetCategory}
                             onChange={(e) => setTargetCategory(e.target.value)}
                             className="w-full bg-white border border-indigo-100 rounded-2xl px-5 py-4 text-sm font-bold text-indigo-900 outline-none focus:ring-4 focus:ring-indigo-200/20 transition-all shadow-sm appearance-none"
                             title="Seleccionar Categoria"
                           >
                              {CATEGORIES.map(c => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                              ))}
                           </select>
                        </div>
                     </div>

                     <button 
                       onClick={handleSaveToIdentity}
                       disabled={saved || !targetName}
                       className={`w-full py-5 rounded-2xl text-xs font-black uppercase tracking-[0.3em] transition-all flex items-center justify-center gap-3 shadow-xl ${
                         saved ? 'bg-green-500 text-white cursor-default' : (!targetName ? 'bg-slate-200 text-slate-400' : 'bg-indigo-600 text-white hover:bg-slate-900 active:scale-95 shadow-indigo-200')
                       }`}
                     >
                        {saved ? (
                          <><CheckCircle2 size={18} /> Identidad Sincronizada</>
                        ) : (
                          <><Zap size={18} /> Consolidar Identidad</>
                        )}
                     </button>
                  </div>

               </div>
            )}
         </div>

      </div>

      {/* FOOTER */}
      <div className="max-w-6xl mx-auto w-full mt-12 border-t border-slate-200 pt-8 text-center flex items-center justify-center gap-4 opacity-50">
         <Shield size={16} className="text-slate-400" />
         <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.4em]">
           Clinical Vision Engine — Sovereignty Module 5.0
         </p>
      </div>

    </div>
  );
}
