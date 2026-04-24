import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Film, Play, Download, Sparkles, Layers, Image as ImageIcon, 
  Trash2, Plus, Zap, CheckCircle, Loader2, ChevronRight, Wand2, Music, Clapperboard,
  Settings, MessageSquare, Mic, Volume2, Move, Frame, Repeat, FastForward, ShieldCheck
} from 'lucide-react';

interface GalleryItem {
  id: string;
  url: string;
  dna_prompt?: string;
  analysis?: any;
}

interface BrandProfile {
  id: string;
  name: string;
  gallery: (GalleryItem | string)[];
  category: string;
  voice?: string;
  mood?: string;
}

interface MotionStudioUIProps {
  initialBrand: BrandProfile | null;
  onBack: () => void;
  allBrands: BrandProfile[];
}

export default function MotionStudioUI({ initialBrand, onBack, allBrands }: MotionStudioUIProps) {
  const [selectedBrand, setSelectedBrand] = useState<BrandProfile | null>(initialBrand);
  const [selectedAssets, setSelectedAssets] = useState<GalleryItem[]>([]);
  const [productionMode, setProductionMode] = useState<'standard' | 'keyframes' | 'motion_transfer'>('standard');
  const [generating, setGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [productionPrompt, setProductionPrompt] = useState('');
  
  // Parámetros Cinematográficos
  const [motionIntensity, setMotionIntensity] = useState(5);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [resolution, setResolution] = useState('4K');

  // Parámetros de Audio (Eleven Labs Style)
  const [audioStability, setAudioStability] = useState(0.5);
  const [audioSimilarity, setAudioSimilarity] = useState(0.75);
  const [audioStyleExaggeration, setAudioStyleExaggeration] = useState(0.2);

  // Filtrar solo las marcas que tienen galería
  const brandsWithAssets = allBrands.filter(b => b.gallery && b.gallery.length > 0);

  const toggleAssetSelection = (item: GalleryItem) => {
    if (productionMode === 'keyframes') {
       if (selectedAssets.length >= 2 && !selectedAssets.find(a => a.id === item.id)) return;
    }
    const isSelected = selectedAssets.find(a => a.id === item.id);
    if (isSelected) {
      setSelectedAssets(selectedAssets.filter(a => a.id !== item.id));
    } else {
      setSelectedAssets([...selectedAssets, item]);
    }
  };

  const generateStoryboard = () => {
    if (selectedAssets.length === 0 || !selectedBrand) return;
    
    const identityAnchor = `CONCORDANCIA ABSOLUTA DE IDENTIDAD: El sujeto debe mantener exactamente la fisionomía de ${selectedBrand.name}. `;
    const dnaPrompts = selectedAssets
      .map(a => a.dna_prompt || (typeof a === 'string' ? '' : a.analysis?.description))
      .filter(p => p)
      .join(productionMode === 'keyframes' ? ' --> TRANSICIÓN FLUIDA A --> ' : ' | NEXT SEQUENCE: ');

    const finalPrompt = `${identityAnchor}\nESTRATEGIA NARRATIVA: ${dnaPrompts}.\nCINEMATOGRAFÍA: Movimiento de cámara profesional, ${motionIntensity}/10 intensidad, estilo fotorrealista, iluminación cinemática.`;
    
    setProductionPrompt(finalPrompt);
  };

  const startProduction = async () => {
    if (!productionPrompt) return;
    try {
      setGenerating(true);
      setVideoUrl(null);
      await new Promise(resolve => setTimeout(resolve, 6000));
      setVideoUrl('https://assets.mixkit.co/videos/preview/mixkit-stars-in-the-night-sky-over-a-mountain-4848-large.mp4');
    } catch (err) {
      console.error("Error en producción de video:", err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#020617] text-white h-full overflow-hidden animate-fade-in font-sans">
      {/* HEADER DE PRODUCCIÓN CINEMATOGRÁFICA */}
      <div className="px-12 py-8 bg-slate-900/40 backdrop-blur-3xl border-b border-white/5 flex justify-between items-center z-10 shadow-2xl">
        <div className="flex items-center gap-6">
           <button onClick={onBack} title="Volver al Studio" className="p-4 hover:bg-white/5 rounded-[22px] transition-all text-slate-400 border border-transparent hover:border-white/10"><ArrowLeft size={20} /></button>
           <div>
              <div className="flex items-center gap-3">
                 <Clapperboard className="text-indigo-500 animate-pulse" size={26} />
                 <h1 className="text-3xl font-black tracking-tighter uppercase leading-none bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Motion Studio v5.0</h1>
                 <span className="px-3 py-1 bg-indigo-600/20 border border-indigo-600/30 text-indigo-400 rounded-full text-[9px] font-black uppercase tracking-widest">Master Mode</span>
              </div>
              <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.4em] mt-2 ml-1">High-Fidelity AI Cinematography Director</p>
           </div>
        </div>
        
        <div className="flex items-center gap-6">
           <div className="flex bg-slate-900/80 border border-white/5 rounded-2xl p-1.5 shadow-inner">
              {[
                {id: 'standard', label: 'IMG 2 VIDEO', icon: <ImageIcon size={14} />},
                {id: 'keyframes', label: 'FIRST & LAST', icon: <Frame size={14} />},
                {id: 'motion_transfer', label: 'MOTION TRANS', icon: <Repeat size={14} />}
              ].map(mode => (
                 <button 
                   key={mode.id}
                   onClick={() => { setProductionMode(mode.id as any); setSelectedAssets([]); }}
                   className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-[10px] font-black transition-all ${productionMode === mode.id ? 'bg-indigo-600 text-white shadow-xl' : 'text-slate-500 hover:text-slate-300'}`}
                 >
                    {mode.icon} {mode.label}
                 </button>
              ))}
           </div>
           <button 
             onClick={startProduction}
             disabled={generating || !productionPrompt}
             className={`flex items-center gap-3 px-12 py-4 rounded-[24px] text-[12px] font-black uppercase transition-all ${
               productionPrompt ? 'bg-indigo-600 hover:bg-indigo-500 shadow-[0_15px_40px_-10px_rgba(79,70,229,0.5)] active:scale-95' : 'bg-slate-800 text-slate-600 cursor-not-allowed opacity-50'
             }`}
           >
              {generating ? <Loader2 className="animate-spin" size={18} /> : <Zap size={18} />} 
              Render Master
           </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* SIDEBAR: CONTROL CINEMATOGRÁFICO Y AUDIO */}
        <div className="w-[480px] border-r border-white/5 flex flex-col p-10 overflow-y-auto custom-scrollbar bg-slate-900/20 backdrop-blur-sm">
           <div className="mb-10 p-6 bg-indigo-600/5 border border-indigo-600/20 rounded-[32px] relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10"><ShieldCheck size={60} /></div>
              <label className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-3 block">Anclaje de Identidad</label>
              <select 
                title="Seleccionar Identidad Protagonista"
                className="w-full bg-slate-900/80 border border-white/10 rounded-2xl p-5 text-[12px] font-black text-white appearance-none outline-none focus:ring-2 focus:ring-indigo-500"
                value={selectedBrand?.id || ''}
                onChange={(e) => {
                   const b = brandsWithAssets.find(x => x.id === e.target.value);
                   setSelectedBrand(b || null);
                   setSelectedAssets([]);
                }}
              >
                 <option value="">(Selecciona Protagonista)</option>
                 {brandsWithAssets.map(b => (
                    <option key={b.id} value={b.id}>{b.name.toUpperCase()}</option>
                 ))}
              </select>
           </div>

           {selectedBrand && (
              <div className="space-y-10">
                 {/* ASSET SELECTOR */}
                 <section>
                    <div className="flex justify-between items-center mb-6">
                       <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">
                          {productionMode === 'keyframes' ? 'Keyframes (Max 2)' : 'DNA Pool Selection'} ({selectedAssets.length})
                       </label>
                       {selectedAssets.length > 0 && (
                          <button onClick={generateStoryboard} className="text-[10px] font-black text-indigo-400 uppercase hover:text-indigo-300 flex items-center gap-1">
                             Sintetizar Guion <Sparkles size={12} />
                          </button>
                       )}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                       {selectedBrand.gallery.map((item, idx) => {
                          const itemObj = typeof item === 'string' ? { url: item, id: String(idx) } : item;
                          const isSelected = selectedAssets.find(a => a.id === itemObj.id);
                          return (
                             <div 
                               key={idx}
                               onClick={() => toggleAssetSelection(itemObj as GalleryItem)}
                               className={`group aspect-video rounded-2xl overflow-hidden cursor-pointer relative transition-all duration-500 border-4 ${
                                 isSelected ? 'border-indigo-600 scale-[0.98] shadow-2xl shadow-indigo-600/20' : 'border-transparent opacity-50 hover:opacity-100 hover:border-white/10'
                               }`}
                             >
                                <img src={itemObj.url} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" alt="Identity Asset" />
                                {isSelected && (
                                   <div className="absolute inset-0 bg-indigo-600/20 flex items-center justify-center">
                                      <div className="bg-white text-indigo-600 rounded-full p-2 shadow-xl"><CheckCircle size={20} /></div>
                                   </div>
                                )}
                                <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-md px-2 py-1 rounded-lg text-[8px] font-black text-white/80 opacity-0 group-hover:opacity-100 transition-opacity">ID_{idx+1}</div>
                             </div>
                          );
                       })}
                    </div>
                 </section>

                 {/* VIDEO PARAMETERS */}
                 <section className="bg-white/5 rounded-[32px] p-8 border border-white/5 space-y-6">
                    <div className="flex items-center gap-2 mb-4 text-indigo-400">
                       <Settings size={16} />
                       <h4 className="text-[11px] font-black uppercase tracking-widest">Cinematography Params</h4>
                    </div>
                    
                    <div>
                       <div className="flex justify-between mb-3"><span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Motion Intensity</span><span className="text-[10px] text-indigo-400">{motionIntensity}/10</span></div>
                       <input title="Intensidad de Movimiento Cinemático" type="range" min="1" max="10" value={motionIntensity} onChange={(e) => setMotionIntensity(Number(e.target.value))} className="w-full h-1.5 bg-slate-800 rounded-full appearance-none accent-indigo-600" />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                       <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                          <span className="text-[8px] font-black text-slate-500 uppercase block mb-2">Resolution</span>
                          <select title="Resolución de Salida" className="bg-transparent text-[11px] font-black text-white w-full outline-none" value={resolution} onChange={(e) => setResolution(e.target.value)}>
                             <option>4K ULTRA</option><option>8K MASTER</option><option>PRORES 422</option>
                          </select>
                       </div>
                       <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                          <span className="text-[8px] font-black text-slate-500 uppercase block mb-2">Aspect Ratio</span>
                          <select title="Relación de Aspecto (Formato)" className="bg-transparent text-[11px] font-black text-white w-full outline-none" value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)}>
                             <option>16:9 CINEMA</option><option>9:16 VERTICAL</option><option>1:1 SOCIAL</option><option>2.39:1 SCOPE</option>
                          </select>
                       </div>
                    </div>
                 </section>

                 {/* AUDIO DESIGN (ELEVEN LABS) */}
                 <section className="bg-white/5 rounded-[32px] p-8 border border-white/5 space-y-8">
                    <div className="flex items-center justify-between mb-2">
                       <div className="flex items-center gap-2 text-rose-400">
                          <Music size={16} />
                          <h4 className="text-[11px] font-black uppercase tracking-widest">Voice & SFX Design</h4>
                       </div>
                       <span className="text-[8px] font-black text-slate-500 bg-white/5 px-2 py-1 rounded-full uppercase tracking-tighter">Powered by ElevenLabs v3</span>
                    </div>

                    <div className="space-y-6">
                       <div>
                          <div className="flex justify-between mb-3"><span className="text-[9px] font-bold text-slate-400 uppercase">Stability</span><span className="text-[9px] text-rose-400">{(audioStability * 100).toFixed(0)}%</span></div>
                          <input title="Estabilidad de Voz" type="range" step="0.1" min="0" max="1" value={audioStability} onChange={(e) => setAudioStability(Number(e.target.value))} className="w-full h-1 bg-slate-800 rounded-full appearance-none accent-rose-500" />
                          <p className="text-[8px] text-slate-500 mt-2 italic">Valores bajos = mayor expresividad emocional.</p>
                       </div>
                       <div>
                          <div className="flex justify-between mb-3"><span className="text-[9px] font-bold text-slate-400 uppercase">Similarity</span><span className="text-[9px] text-rose-400">{(audioSimilarity * 100).toFixed(0)}%</span></div>
                          <input title="Similitud de Voz (Fidelidad)" type="range" step="0.1" min="0" max="1" value={audioSimilarity} onChange={(e) => setAudioSimilarity(Number(e.target.value))} className="w-full h-1 bg-slate-800 rounded-full appearance-none accent-rose-500" />
                       </div>
                    </div>

                    <div className="p-4 bg-black/40 rounded-2xl border border-white/5 flex items-center gap-4">
                       <div className="p-3 bg-rose-500/10 rounded-xl text-rose-400"><Mic size={18} /></div>
                       <div className="flex-1">
                          <p className="text-[9px] font-black text-slate-500 uppercase">Voice Matching</p>
                          <p className="text-[11px] font-bold text-white truncate">{selectedBrand.voice || 'Cargar Voz de Referencia...'}</p>
                       </div>
                       <ChevronRight size={14} className="text-slate-600" />
                    </div>
                 </section>

                 {/* FINAL SCRIPT */}
                 <section>
                    <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-4 block">Guion Técnico de Producción</label>
                    <textarea 
                      className="w-full h-48 bg-black/60 border border-indigo-600/20 rounded-[32px] p-8 text-[12px] font-mono text-emerald-400 outline-none resize-none focus:border-indigo-500 transition-all shadow-inner leading-relaxed"
                      value={productionPrompt}
                      onChange={(e) => setProductionPrompt(e.target.value)}
                      placeholder="Selecciona secuencias de ADN para sintetizar el guion cinemático..."
                    />
                 </section>
              </div>
           )}
        </div>

        {/* ÁREA DE VISUALIZACIÓN / MONITOR DE MASTERIZACIÓN */}
        <div className="flex-1 p-12 bg-black flex flex-col items-center justify-center relative overflow-hidden">
           {/* SCANLINES & OVERLAY EFFECT */}
           <div className="absolute inset-0 opacity-5 pointer-events-none z-10 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%]" />
           <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-transparent to-transparent opacity-60 z-10" />

           <div className={`relative w-full max-w-6xl rounded-[48px] overflow-hidden border-[12px] border-white/5 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] transition-all duration-1000 ${generating ? 'scale-[0.97] opacity-60 grayscale' : 'scale-100'}`}>
              {videoUrl ? (
                 <div className="relative group">
                    <video src={videoUrl} autoPlay loop muted controls className="w-full aspect-video object-cover" />
                    <div className="absolute top-8 left-8 flex gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                       <div className="px-4 py-2 bg-black/60 backdrop-blur-xl border border-white/10 rounded-full flex items-center gap-2 text-[9px] font-black uppercase text-white">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" /> REC MASTER
                       </div>
                    </div>
                 </div>
              ) : (
                 <div className="aspect-video bg-slate-900/40 flex flex-col items-center justify-center gap-8 relative">
                    {generating ? (
                       <div className="flex flex-col items-center gap-8">
                          <div className="relative">
                             <div className="w-24 h-24 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin" />
                             <div className="absolute inset-0 flex items-center justify-center text-indigo-500"><Zap size={32} /></div>
                          </div>
                          <div className="text-center space-y-3">
                             <p className="text-[12px] font-black uppercase tracking-[0.6em] text-indigo-400 animate-pulse">Interpolando Fotogramas Maestro</p>
                             <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Calculando trayectoria narrativa...</p>
                          </div>
                       </div>
                    ) : (
                       <>
                          <div className="w-32 h-32 bg-white/5 rounded-full flex items-center justify-center text-slate-700 border border-white/5 shadow-inner">
                             <Film size={60} className="text-slate-800" />
                          </div>
                          <div className="text-center max-w-xl mx-auto space-y-4">
                             <h4 className="text-3xl font-black uppercase tracking-tighter bg-gradient-to-b from-white to-slate-600 bg-clip-text text-transparent">Monitor de Masterización</h4>
                             <p className="text-base text-slate-500 font-medium leading-relaxed">Configura el raccord visual en el panel izquierdo. Utiliza el modo <span className="text-indigo-400">First & Last Frame</span> para un control total del movimiento cinemático.</p>
                          </div>
                       </>
                    )}
                 </div>
              )}

              {videoUrl && !generating && (
                 <div className="absolute bottom-10 right-10 flex gap-4 animate-slide-up">
                    <button className="flex items-center gap-4 px-10 py-5 bg-white text-black rounded-[28px] text-[13px] font-black uppercase hover:bg-slate-100 shadow-2xl transition-all active:scale-95">
                       <Download size={20} /> Exportar Master 4K
                    </button>
                    <button onClick={() => setVideoUrl(null)} title="Descartar Toma" className="p-5 bg-white/10 backdrop-blur-2xl border border-white/20 rounded-[28px] text-white hover:bg-red-500/20 hover:text-red-400 transition-all">
                       <Trash2 size={20} />
                    </button>
                 </div>
              )}
           </div>

           {/* STATUS DASHBOARD */}
           <div className="mt-16 grid grid-cols-4 gap-12 text-slate-500">
              <div className="flex flex-col gap-2">
                 <span className="text-[8px] font-black uppercase tracking-widest text-slate-600">Pipeline Protocol</span>
                 <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(79,70,229,1)]" />
                    <span className="text-[11px] font-black text-slate-300 uppercase tracking-widest">SOVEREIGN_ON</span>
                 </div>
              </div>
              <div className="flex flex-col gap-2">
                 <span className="text-[8px] font-black uppercase tracking-widest text-slate-600">Raccord Integrity</span>
                 <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-[11px] font-black text-slate-300 uppercase tracking-widest">99.8% STABLE</span>
                 </div>
              </div>
              <div className="flex flex-col gap-2">
                 <span className="text-[8px] font-black uppercase tracking-widest text-slate-600">Audio Sync</span>
                 <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-rose-500" />
                    <span className="text-[11px] font-black text-slate-300 uppercase tracking-widest">STUDIO_LOCK</span>
                 </div>
              </div>
              <div className="flex flex-col gap-2">
                 <span className="text-[8px] font-black uppercase tracking-widest text-slate-600">Compute Hub</span>
                 <div className="flex items-center gap-3">
                    <FastForward size={14} className="text-slate-400" />
                    <span className="text-[11px] font-black text-slate-300 uppercase tracking-widest">LOCAL_GPU_ACTIVE</span>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
