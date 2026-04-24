import React, { useState, useRef, useEffect } from 'react';
import {
  PenTool, Layers, Instagram, Linkedin, Twitter, Mail,
  RefreshCw, Shield, Copy, Check, ChevronRight, Sparkles,
  AlertTriangle, Loader2, Video, Film, Users, BookOpen, PlusCircle, X,
  Monitor, Zap, Wand2, Type, Globe, ChevronDown, Camera, Image as ImageIcon
} from 'lucide-react';

interface Brand {
  id: string;
  name: string;
  category: string;
  voice: string;
  mood: string;
}

interface Reference {
  id: string;
  type: 'image' | 'video';
  data: string; // base64
  preview: string;
}

interface ContentMachineUIProps {
  onBack?: () => void;
}

export default function ContentMachineUI({ onBack }: ContentMachineUIProps) {
  // Configuración de Generación
  const [strategy, setStrategy] = useState<'standard' | 'nexus' | 'radar'>('standard');
  const [format, setFormat] = useState<string>('instagram');
  const [optimization, setOptimization] = useState<'master' | 'luma' | 'runway' | 'kling'>('master');
  
  // Identidad
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrandId, setSelectedBrandId] = useState<string>('AlegrIA');
  const [loadingBrands, setLoadingBrands] = useState(false);
  
  // Referencias (3-Slot Matrix)
  const [references, setReferences] = useState<Reference[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Estado de Generación
  const [topic, setTopic] = useState('');
  const [lyrics, setLyrics] = useState('');
  const [output, setOutput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  
  // Imagenes Generadas
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Cargar identidades al iniciar
  useEffect(() => {
    fetchBrands();
  }, []);

  const fetchBrands = async () => {
    setLoadingBrands(true);
    setError('');
    try {
      const res = await fetch('/api/brand/all');
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Error de servidor (${res.status}): ${errorText}`);
      }
      const data = await res.json();
      if (data.brands) {
        setBrands(Object.values(data.brands));
      }
    } catch (e: any) {
      console.error("Error cargando identidades:", e);
      setError(`No se pudieron cargar las identidades: ${e.message}`);
    } finally {
      setLoadingBrands(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    if (references.length >= 3) {
      setError("Máximo 3 referencias permitidas.");
      return;
    }

    Array.from(files).slice(0, 3 - references.length).forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        const type = file.type.startsWith('video') ? 'video' : 'image';
        setReferences(prev => [...prev, {
          id: Math.random().toString(36).substr(2, 9),
          type,
          data: base64,
          preview: base64
        }]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeReference = (id: string) => {
    setReferences(prev => prev.filter(r => r.id !== id));
  };

  const handleGenerate = async (isRefresh = false) => {
    if (!topic.trim() && !lyrics.trim()) { textareaRef.current?.focus(); return; }
    setGenerating(true);
    if (!isRefresh) {
      setOutput('');
      setGeneratedImageUrl(null);
    }
    setError('');
    
    try {
      const res = await fetch('/api/anima/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy,
          format,
          topic: topic.trim(),
          lyrics: lyrics.trim(),
          brand_id: selectedBrandId,
          optimization,
          references: references.map(r => ({ type: r.type, data: r.data }))
        }),
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        let message = `Error de servidor (${res.status})`;
        try {
          const errData = JSON.parse(errorText);
          message = errData.message || message;
        } catch(ip) { /* no json */ }
        throw new Error(message);
      }

      const data = await res.json();
      if (data.status === 'error') throw new Error(data.message || 'Error en el motor central');
      
      setOutput(data.response || '');
    } catch (e: any) {
      setError(`Error de producción: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateVisual = async () => {
    if (!output) return;
    setGeneratingImage(true);
    setError('');
    
    try {
      const promptToUse = output.split('[MASTER]:')[1]?.split('\n')[0] || topic || output.slice(0, 300);
      
      const res = await fetch('/api/anima/generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptToUse, brand_id: selectedBrandId })
      });
      
      const data = await res.json();
      if (data.status === 'error') throw new Error(data.message);
      setGeneratedImageUrl(data.image_url);
    } catch (e: any) {
      setError(`Error en visualización: ${e.message}`);
    } finally {
      setGeneratingImage(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const strategies = [
    { id: 'standard', name: 'Estándar', desc: 'Voz activa. Precisión total.', icon: <Zap size={16} /> },
    { id: 'nexus', name: 'Nexus', desc: 'Conexiones profundas.', icon: <Layers size={16} /> },
    { id: 'radar', name: 'Radar', desc: 'Tendencias y viralidad.', icon: <Globe size={16} /> },
  ];

  const formats = [
    { id: 'instagram', name: 'Social Post', icon: <Instagram size={15} /> },
    { id: 'video', name: 'Video AI', icon: <Video size={15} /> },
    { id: 'music_video', name: 'Video Musical', icon: <Monitor size={15} /> },
    { id: 'interview', name: 'Entrevista', icon: <Users size={15} /> },
    { id: 'tutorial', name: 'Tutorial', icon: <BookOpen size={15} /> },
  ];

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden animate-fade-in font-sans">
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-10">

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10">
          
          {/* COLUMNA IZQUIERDA: CONFIGURACIÓN */}
          <div className="lg:col-span-4 space-y-10">
            
            <div className="flex items-center gap-5 mb-12">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-[2rem] flex items-center justify-center shadow-2xl shadow-purple-600/20">
                <PenTool className="text-white w-8 h-8" />
              </div>
              <div>
                <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Content Machine</h2>
                <div className="flex items-center gap-2 mt-1">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Motor Operativo v2.6 · Online</p>
                </div>
              </div>
            </div>

            {/* IDENTIDAD */}
            <div className="operative-card p-6 border-slate-800 bg-[#162129]">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] block mb-4">Seleccionar Identidad</span>
              <select 
                value={selectedBrandId}
                title="Seleccionar Identidad de Marca"
                onChange={(e) => setSelectedBrandId(e.target.value)}
                className="w-full bg-[#0b141a] border border-slate-800 rounded-xl p-4 text-white font-bold text-xs outline-none focus:ring-2 focus:ring-purple-500 transition-all cursor-pointer appearance-none"
              >
                {brands.map(b => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>

            {/* ESTRATEGIA */}
            <div className="grid grid-cols-3 gap-3">
              {strategies.map(s => (
                <button
                  key={s.id}
                  onClick={() => setStrategy(s.id as any)}
                  className={`p-4 rounded-2xl border transition-all flex flex-col items-center gap-2 ${
                    strategy === s.id ? 'bg-purple-600 border-purple-500 text-white' : 'bg-[#162129] border-slate-800 text-slate-500 hover:bg-slate-800/50'
                  }`}
                >
                  {s.icon}
                  <span className="text-[9px] font-black uppercase tracking-tighter">{s.name}</span>
                </button>
              ))}
            </div>

            {/* FORMATO */}
            <div className="grid grid-cols-2 gap-3">
              {formats.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  className={`p-4 rounded-2xl border transition-all flex items-center justify-center gap-3 ${
                    format === f.id ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-[#162129] border-slate-800 text-slate-500 hover:bg-slate-800/50'
                  }`}
                >
                  {f.icon}
                  <span className="text-[9px] font-black uppercase tracking-tighter">{f.name}</span>
                </button>
              ))}
            </div>

            {/* REFERENCIAS (3-Ref Matrix) */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Referencias Vis uales</span>
                <span className="text-[9px] text-purple-400 font-bold uppercase">{references.length}/3</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {references.map(ref => (
                  <div key={ref.id} className="relative aspect-square rounded-2xl overflow-hidden border border-slate-800 bg-slate-900 group">
                    <img src={ref.preview} alt="Referencia" className="w-full h-full object-cover" />
                    <button 
                      onClick={() => removeReference(ref.id)}
                      title="Eliminar referencia"
                      className="absolute inset-0 bg-red-600/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
                {references.length < 3 && (
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    title="Añadir referencia visual o de video"
                    className="aspect-square rounded-2xl border-2 border-dashed border-slate-800 flex flex-col items-center justify-center text-slate-700 hover:border-purple-500 hover:text-purple-500 transition-all"
                  >
                    <PlusCircle size={24} />
                  </button>
                )}
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                className="hidden" 
                multiple 
                accept="image/*,video/*" 
                title="Subir archivos de referencia"
              />
            </div>

          </div>

          {/* COLUMNA DERECHA: PROMPT & OUTPUT */}
          <div className="lg:col-span-8 space-y-8">
            
            <div className="operative-card p-8 bg-[#162129] border-slate-800 relative overflow-hidden">
               <div className="relative z-10 space-y-6">
                 <textarea
                  ref={textareaRef}
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  title="Prompts y Temas de Producción"
                  placeholder="Describe la idea, el tópico o el mensaje que quieres procesar..."
                  rows={4}
                  className="w-full bg-[#0b141a] border border-slate-800 rounded-3xl p-8 text-white text-lg placeholder-slate-700 font-mono leading-relaxed outline-none focus:ring-4 focus:ring-purple-500/10 transition-all"
                />
                
                <button
                  onClick={() => handleGenerate()}
                  disabled={generating || !topic.trim()}
                  className="w-full py-6 rounded-[2.5rem] bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-30 transition-all flex items-center justify-center gap-4 font-black text-white text-xs uppercase tracking-[0.3em] shadow-2xl shadow-purple-600/30"
                >
                  {generating ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
                  {generating ? 'Engine Sincronizando...' : 'Consolidar Producción'}
                </button>
               </div>
            </div>

            {/* RESULTADO */}
            {output && (
              <div className="operative-card p-8 bg-[#162129] border-slate-800 animate-fade-in-up">
                <div className="flex justify-between items-center mb-8 border-b border-slate-800 pb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-purple-600/10 flex items-center justify-center border border-purple-500/20">
                      <Zap size={16} className="text-purple-500" />
                    </div>
                    <span className="text-xs font-black text-white uppercase tracking-widest">ADN_OPERATIVO</span>
                  </div>
                  <div className="flex gap-2">
                    <button 
                      onClick={handleGenerateVisual}
                      disabled={generatingImage}
                      title="Generar Vista Previa Visual"
                      className="px-6 py-2.5 rounded-full bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-indigo-500 transition-all flex items-center gap-2 shadow-lg"
                    >
                      {generatingImage ? <Loader2 className="animate-spin" size={14} /> : <ImageIcon size={14} />}
                      Visualizar
                    </button>
                    <button 
                      onClick={handleCopy}
                      title="Copiar ADN Operativo"
                      className="p-2.5 rounded-full bg-slate-800 text-slate-400 hover:text-white transition-all border border-slate-700"
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-10">
                   <div className="md:col-span-7">
                     <pre className="text-sm text-slate-100 font-mono whitespace-pre-wrap leading-relaxed selection:bg-purple-500/30">{output}</pre>
                   </div>
                   
                   <div className="md:col-span-5">
                      <div className="aspect-[4/5] rounded-[3rem] border-4 border-slate-800 overflow-hidden bg-black/40 relative group shadow-2xl">
                         {generatedImageUrl ? (
                           <img src={generatedImageUrl} alt="Generated Asset" className="w-full h-full object-cover animate-fade-in" />
                         ) : (
                           <div className="w-full h-full flex flex-col items-center justify-center opacity-20">
                              <ImageIcon size={40} className="text-slate-600 mb-4" />
                              <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Sin Visualización</span>
                           </div>
                         )}
                         {generatingImage && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center">
                               <div className="w-12 h-12 border-4 border-t-indigo-600 border-slate-800 rounded-full animate-spin" />
                            </div>
                         )}
                      </div>
                   </div>
                </div>
              </div>
            )}

            {error && (
              <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-3xl flex items-center gap-4 text-red-500">
                <AlertTriangle size={20} />
                <span className="text-xs font-bold font-mono">{error}</span>
              </div>
            )}

          </div>
        </div>
      </div>
      
      {/* FOOTER BAR */}
      <div className="px-10 py-5 border-t border-slate-800 bg-black/20 flex justify-between items-center text-slate-700">
        <div className="flex items-center gap-2">
          <Shield size={12} />
          <span className="text-[9px] font-black uppercase tracking-widest">ALEGR-IA OS Protocol · v2.6 Sovereign</span>
        </div>
        <div className="flex gap-4">
          <span className="text-[9px] font-bold">READY_FOR_DIRECTOR</span>
        </div>
      </div>
    </div>
  );
}
