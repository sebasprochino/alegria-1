import React, { useState, useEffect, useRef } from 'react';
import { 
  Save, Plus, Globe, Zap, Image as ImageIcon, CheckCircle, ArrowLeft, Loader2, 
  Layout, MessageSquare, Info, ExternalLink, User, Package, Lightbulb, 
  UserCircle, Tv, Briefcase, Calendar, Trash2, Link as LinkIcon, Terminal, FileText, ChevronRight,
  Layers, ChevronDown, FolderOpen, MoreHorizontal, Sparkles, Filter, X, Maximize2, Play, Download,
  Upload, Film, Music
} from 'lucide-react';
import MotionStudioUI from './MotionStudioUI';

interface CustomField {
  id: string;
  label: string;
  type: 'text' | 'textarea' | 'link' | 'prompt';
  value: string;
}

interface GalleryItem {
  id: string;
  url: string;
  analysis?: any;
  dna_prompt?: string;
  created_at: string;
  label?: string;
}

interface BrandProfile {
  id: string;
  name: string;
  category: string;
  voice: string;
  mood: string;
  context?: string;
  palette: string[];
  gallery: (GalleryItem | string)[];
  links: string[];
  custom_fields?: CustomField[];
  parent_id?: string;
  updated_at?: string;
}

interface BrandStudioUIProps {
  onBack: () => void;
}

const CATEGORIES = [
  { id: 'brand', name: 'MARCA / PROYECTO', icon: <Zap size={12} />, activeColor: 'bg-indigo-600 text-white border-indigo-600', shadowColor: 'shadow-indigo-600/20' },
  { id: 'persona', name: 'PERSONA', icon: <User size={12} />, activeColor: 'bg-orange-500 text-white border-orange-500', shadowColor: 'shadow-orange-500/20' },
  { id: 'producto', name: 'PRODUCTO', icon: <Package size={12} />, activeColor: 'bg-teal-500 text-white border-teal-500', shadowColor: 'shadow-teal-500/20' },
  { id: 'idea', name: 'IDEA', icon: <Lightbulb size={12} />, activeColor: 'bg-purple-500 text-white border-purple-500', shadowColor: 'shadow-purple-500/20' },
  { id: 'artista', name: 'ARTISTA', icon: <UserCircle size={12} />, activeColor: 'bg-rose-500 text-white border-rose-500', shadowColor: 'shadow-rose-500/20' },
  { id: 'medios', name: 'MEDIOS', icon: <Tv size={12} />, activeColor: 'bg-blue-500 text-white border-blue-500', shadowColor: 'shadow-blue-500/20' },
  { id: 'servicios', name: 'SERVICIOS', icon: <Briefcase size={12} />, activeColor: 'bg-emerald-500 text-white border-emerald-500', shadowColor: 'shadow-emerald-500/20' },
  { id: 'eventos', name: 'EVENTOS', icon: <Calendar size={12} />, activeColor: 'bg-orange-600 text-white border-orange-600', shadowColor: 'shadow-orange-600/20' },
];

export default function BrandStudioUI({ onBack }: BrandStudioUIProps) {
  const [view, setView] = useState<'dashboard' | 'detail' | 'motion_studio'>('dashboard');
  const [allBrands, setAllBrands] = useState<BrandProfile[]>([]);
  const [brand, setBrand] = useState<BrandProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showFieldMenu, setShowFieldMenu] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [selectedAsset, setSelectedAsset] = useState<{item: GalleryItem, index: number} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Helper for dynamic styles
  const getCatStyles = (logoColor: string) => ({
    backgroundColor: `${logoColor}20`,
    borderColor: `${logoColor}30`
  } as React.CSSProperties);

  useEffect(() => {
    fetchAllBrands();
  }, []);

  const fetchAllBrands = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/brand/all');
      const data = await res.json();
      const brandsList = Object.values(data.brands) as BrandProfile[];
      setAllBrands(brandsList);
    } catch (err) {
      console.error("Error fetching brands:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnterBrand = (b: BrandProfile) => {
    setBrand(b);
    setView('detail');
  };

  const handleUpdate = (field: keyof BrandProfile, value: any) => {
    if (!brand) return;
    setBrand({ ...brand, [field]: value });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !brand) return;
    const files = Array.from(e.target.files);
    
    setUploading(true);
    for (const file of files) {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const base64 = event.target?.result as string;
        try {
          const res = await fetch('/api/brand/add-asset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              brand_id: brand.id,
              image_data: base64
            })
          });
          const data = await res.json();
          if (data.status === 'ok') {
            setBrand(prev => {
               if (!prev) return null;
               return { ...prev, gallery: [data.asset, ...prev.gallery] };
            });
          }
        } catch (err) {
          console.error("Error subiendo activo:", err);
        }
      };
      reader.readAsDataURL(file);
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const createNewElement = () => {
    const newId = `id_${Date.now()}`;
    const newBrand: BrandProfile = {
      id: newId,
      name: 'Nueva Identidad',
      category: 'idea',
      voice: '',
      mood: '',
      palette: ['#7c3aed'],
      gallery: [],
      links: [],
      custom_fields: []
    };
    setBrand(newBrand);
    setView('detail');
  };

  const addCustomField = (type: CustomField['type']) => {
    if (!brand) return;
    const newField: CustomField = {
      id: crypto.randomUUID(),
      label: 'Nuevo Módulo',
      type: type,
      value: ''
    };
    const updatedFields = [...(brand.custom_fields || []), newField];
    setBrand({ ...brand, custom_fields: updatedFields });
    setShowFieldMenu(false);
  };

  const removeCustomField = (id: string) => {
    if (!brand) return;
    const updatedFields = (brand.custom_fields || []).filter(f => f.id !== id);
    setBrand({ ...brand, custom_fields: updatedFields });
  };

  const updateCustomField = (id: string, updates: Partial<CustomField>) => {
    if (!brand) return;
    const updatedFields = (brand.custom_fields || []).map(f => 
      f.id === id ? { ...f, ...updates } : f
    );
    setBrand({ ...brand, custom_fields: updatedFields });
  };

  const saveChanges = async () => {
    if (!brand) return;
    try {
      setSaving(true);
      await fetch('/api/brand/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_id: brand.id,
          updates: brand
        })
      });
      
      const exists = allBrands.find(b => b.id === brand.id);
      if (exists) {
        setAllBrands(allBrands.map(b => b.id === brand.id ? brand : b));
      } else {
        setAllBrands([...allBrands, brand]);
      }
      
      alert("¡Soberanía de Identidad Actualizada!");
    } catch (err) {
      console.error("Error saving brand:", err);
    } finally {
      setSaving(false);
    }
  };

  const removeAsset = (index: number) => {
    if (!brand) return;
    const newGallery = [...brand.gallery];
    newGallery.splice(index, 1);
    handleUpdate('gallery', newGallery);
    setSelectedAsset(null);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#f8fafc]">
        <div className="flex flex-col items-center gap-4">
           <div className="w-12 h-12 rounded-full border-2 border-indigo-600/20 border-t-indigo-600 animate-spin" />
           <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest">Sincronizando Sistema...</p>
        </div>
      </div>
    );
  }

  // --- VISTA MOTION STUDIO ---
  if (view === 'motion_studio') {
     return (
       <MotionStudioUI 
         initialBrand={brand} 
         allBrands={allBrands} 
         onBack={() => setView('detail')} 
       />
     );
  }

  // --- VISTA DASHBOARD ---
  if (view === 'dashboard') {
    return (
      <div className="flex-1 flex flex-col bg-white h-full overflow-hidden animate-fade-in custom-scrollbar overflow-y-auto p-12 font-sans">
         <div className="max-w-7xl mx-auto w-full">
            <div className="flex items-center justify-between mb-16">
               <div>
                  <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase leading-none">Brand Studio</h1>
                  <p className="text-[11px] text-slate-400 font-black uppercase tracking-[0.3em] mt-2">Sovereign Asset Management Center</p>
               </div>
               <button onClick={onBack} className="px-8 py-3 bg-white border border-slate-200 rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-slate-50 shadow-sm transition-all">Terminal</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
               {allBrands.map(b => {
                 const cat = CATEGORIES.find(c => c.id === b.category) || CATEGORIES[0];
                 const thumb = b.gallery && b.gallery.length > 0 
                    ? (typeof b.gallery[0] === 'string' ? b.gallery[0] : b.gallery[0].url) 
                    : null;
                 const parent = allBrands.find(p => p.id === b.parent_id);
                 
                 return (
                    <div key={b.id} onClick={() => handleEnterBrand(b)} className="group bg-white border border-slate-100 rounded-[40px] p-8 hover:shadow-[0_30px_60px_-15px_rgba(0,0,0,0.08)] transition-all duration-500 cursor-pointer flex flex-col h-[380px] relative">
                       <div className="flex items-start justify-between mb-6">
                          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${cat.activeColor} shadow-xl ${cat.shadowColor} group-hover:scale-110 transition-transform`}>{cat.icon}</div>
                          {parent && (
                             <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 border border-slate-100 rounded-full">
                                <Layers size={10} className="text-slate-400" />
                                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{parent.name}</span>
                             </div>
                          )}
                       </div>
                       <h3 className="text-2xl font-black text-slate-900 tracking-tight mb-2 truncate">{b.name}</h3>
                       <p className="text-[12px] text-slate-400 leading-relaxed line-clamp-2 mb-8 font-medium">{b.voice || 'Identidad independiente activa.'}</p>
                       <div className="flex-1 rounded-[32px] bg-slate-50 overflow-hidden relative border border-slate-100/50">
                          {thumb ? <img src={thumb} className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700" alt={b.name} /> : <div className="w-full h-full flex items-center justify-center"><ImageIcon size={32} className="text-slate-200" /></div>}
                       </div>
                    </div>
                 );
               })}
               <div onClick={createNewElement} className="border-4 border-dashed border-slate-100 rounded-[40px] flex flex-col items-center justify-center p-10 hover:border-indigo-400 hover:bg-indigo-50/10 transition-all cursor-pointer group h-[380px]">
                  <div className="w-20 h-20 bg-slate-50 rounded-[30px] flex items-center justify-center text-slate-300 group-hover:bg-white group-hover:text-indigo-600 group-hover:shadow-xl transition-all mb-6"><Plus size={40} /></div>
                  <p className="text-[12px] font-black text-slate-400 uppercase tracking-widest group-hover:text-indigo-600">Nueva Identidad</p>
               </div>
            </div>
         </div>
      </div>
    );
  }

  // --- VISTA DETALLE ---
  const activeCat = CATEGORIES.find(c => c.id === brand?.category) || CATEGORIES[0];

  return (
    <div className="flex-1 flex flex-col bg-[#F8FAFC] h-full overflow-hidden animate-fade-in font-sans">
      {/* MODAL DE ACTIVO (DNA VIEW) */}
      {selectedAsset && (
         <div className="fixed inset-0 z-[100] flex items-center justify-center p-8 backdrop-blur-xl bg-slate-900/40 animate-fade-in">
            <div className="bg-white w-full max-w-6xl h-full max-h-[85vh] rounded-[48px] shadow-2xl overflow-hidden flex flex-col lg:flex-row relative animate-slide-up">
               <button onClick={() => setSelectedAsset(null)} title="Cerrar detalle de activo" className="absolute top-8 right-8 z-20 w-12 h-12 bg-white/10 hover:bg-white/20 backdrop-blur rounded-full flex items-center justify-center text-white transition-all"><X size={24} /></button>

               <div className="lg:w-2/3 bg-slate-900 flex items-center justify-center relative group">
                  <img src={selectedAsset.item.url} className="max-w-full max-h-full object-contain" alt="Asset Detail" />
               </div>

               <div className="lg:w-1/3 flex flex-col p-12 overflow-y-auto custom-scrollbar">
                  <div className="mb-10">
                     <h3 className="text-[10px] font-black text-indigo-600 uppercase tracking-[0.4em] mb-3">Sovereign DNA Asset</h3>
                     <h2 className="text-2xl font-black text-slate-900 tracking-tighter uppercase mb-2">ADN del Activo</h2>
                     <p className="text-[11px] text-slate-400 font-bold uppercase tracking-widest">Identidad Visual Procesada</p>
                  </div>

                  <div className="space-y-8 flex-1">
                     <div>
                        <label className="text-[11px] font-black text-slate-500 uppercase tracking-widest mb-4 block">DNA Prompt (Video Gen)</label>
                        <div className="p-6 bg-slate-900 rounded-3xl border border-white/10 shadow-inner">
                           <p className="text-[13px] text-emerald-400 leading-relaxed font-mono italic">
                              {selectedAsset.item.dna_prompt || selectedAsset.item.analysis?.description || 'Analizando secuencia genética...'}
                           </p>
                        </div>
                        <p className="text-[9px] text-slate-400 mt-3 font-medium">Este prompt asegura la coherencia visual en el generador de video.</p>
                     </div>

                     <div className="grid grid-cols-1 gap-3">
                        <button 
                          onClick={() => setView('motion_studio')}
                          className="w-full flex items-center justify-between p-5 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/20 group"
                        >
                           <div className="flex items-center gap-3">
                              <Film size={18} />
                              <span className="text-[11px] font-black uppercase tracking-widest">Motion Studio Hub</span>
                           </div>
                           <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                        
                        <button title="Eliminar Activo" onClick={() => removeAsset(selectedAsset.index)} className="w-full flex items-center gap-3 p-5 text-red-500 hover:bg-red-50 rounded-2xl transition-all"><Trash2 size={18} /> <span className="text-[11px] font-black uppercase tracking-widest">Eliminar Activo</span></button>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      )}

      <div className="px-12 py-8 bg-white border-b border-slate-200 flex justify-between items-center z-10">
        <div className="flex items-center gap-6">
           <button onClick={() => setView('dashboard')} title="Volver al Panel Principal" className="p-4 hover:bg-slate-50 rounded-[20px] transition-all text-slate-400"><ArrowLeft size={20} /></button>
           <div className="flex flex-col">
              <input title="Nombre de la Identidad Soberana" placeholder="Nombre de la Identidad..." className="text-3xl font-black text-slate-900 tracking-tighter uppercase bg-transparent border-none outline-none focus:ring-0 px-0 min-w-[300px]" value={brand?.name || ''} onChange={(e) => handleUpdate('name', e.target.value)} />
              <div className="flex items-center gap-2 mt-1">
                <span className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${activeCat.activeColor}`}>{activeCat.id}</span>
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Soberanía Activa</span>
              </div>
           </div>
        </div>
        <button onClick={saveChanges} disabled={saving} className="flex items-center gap-2 px-10 py-4 bg-indigo-600 text-white rounded-[22px] text-[12px] font-black uppercase hover:bg-indigo-700 shadow-[0_10px_40px_-10px_rgba(79,70,229,0.4)] disabled:opacity-50 transition-all">
           {saving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />} Guardar Identidad
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 max-w-7xl mx-auto">
          
          <div className="lg:col-span-4 space-y-10">
             <div className="bg-white rounded-[40px] p-10 border border-slate-100 shadow-sm">
                <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-4 block">Vínculo Maestro</label>
                <div className="relative mb-10">
                   <select title="Seleccionar Vínculo Maestro" className="w-full bg-slate-50 border border-slate-100 rounded-[20px] p-5 text-[11px] font-bold text-slate-600 appearance-none outline-none focus:ring-4 focus:ring-indigo-50 transition-all" value={brand?.parent_id || ''} onChange={(e) => handleUpdate('parent_id', e.target.value)}>
                      <option value="">(Sin Vínculo)</option>
                      {allBrands.filter(b => b.id !== brand?.id).map(b => (
                         <option key={b.id} value={b.id}>{b.name} ({b.category})</option>
                      ))}
                   </select>
                   <ChevronDown size={14} className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-300 pointer-events-none" />
                </div>

                <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-4 block">Categoría</label>
                <div className="grid grid-cols-2 gap-3 mb-10">
                   {CATEGORIES.map(cat => (
                      <button key={cat.id} title={`Seleccionar categoría: ${cat.name}`} onClick={() => handleUpdate('category', cat.id)} className={`flex items-center gap-3 py-4 px-4 rounded-[20px] text-[10px] font-black uppercase border-2 transition-all ${brand?.category === cat.id ? cat.activeColor : 'border-slate-50 text-slate-400 bg-slate-50 hover:border-slate-200'}`}>{cat.icon} {cat.name}</button>
                   ))}
                </div>

                <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-4 block">Voz / Arquetipo</label>
                <textarea title="Descripción del Tono de Voz y Arquetipo" className="w-full h-32 bg-slate-50 border border-slate-100 rounded-[24px] p-6 text-[13px] font-medium text-slate-700 outline-none resize-none mb-6 focus:ring-4 focus:ring-indigo-50" value={brand?.voice || ''} onChange={(e) => handleUpdate('voice', e.target.value)} placeholder="Tono comunicacional y personalidad..." />
             </div>

             <div className="space-y-6">
                <button 
                  onClick={() => setView('motion_studio')}
                  className="w-full group relative overflow-hidden bg-slate-900 rounded-[32px] p-10 text-white shadow-2xl hover:scale-[1.02] transition-all"
                >
                   <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:rotate-12 transition-transform"><Film size={80} /></div>
                   <div className="relative z-10">
                      <p className="text-[10px] font-black uppercase tracking-[0.4em] text-indigo-400 mb-2">Creative Production</p>
                      <h4 className="text-2xl font-black uppercase tracking-tighter mb-4">Motion Studio</h4>
                      <div className="flex items-center gap-2 text-[11px] font-bold text-slate-400 group-hover:text-white transition-colors">
                         Abrir Director de Video <ChevronRight size={14} />
                      </div>
                   </div>
                </button>
             </div>
          </div>

          <div className="lg:col-span-8 space-y-12">
             <div className="bg-white rounded-[48px] p-12 border border-slate-100 shadow-sm relative overflow-hidden min-h-[600px]">
                <div className="flex justify-between items-center mb-12 pb-8 border-b border-slate-50">
                   <div>
                      <h3 className="text-2xl font-black text-slate-900 tracking-tight uppercase">Galería de Activos</h3>
                      <p className="text-[11px] text-slate-400 font-black uppercase tracking-[0.3em] mt-3">Identity Assets DNA Pool</p>
                   </div>
                   <div className="flex gap-3">
                      <input 
                        title="Seleccionar archivos de secuencia"
                        type="file" 
                        multiple 
                        accept="image/*" 
                        ref={fileInputRef} 
                        onChange={handleFileUpload} 
                        className="hidden" 
                      />
                      <button 
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading}
                        className="flex items-center gap-3 px-8 py-4 bg-indigo-50 text-indigo-600 rounded-[22px] text-[11px] font-black uppercase tracking-widest hover:bg-indigo-100 transition-all border border-indigo-100"
                      >
                         {uploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
                         Subir Secuencia
                      </button>
                      <button title="Subir Activo Individual" className="p-4 bg-slate-50 border border-slate-100 rounded-[20px] text-slate-400 hover:text-indigo-600 transition-all"><Plus size={20} /></button>
                   </div>
                </div>
                
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-8">
                   {brand?.gallery?.map((item, idx) => {
                      const itemObj = typeof item === 'string' ? { url: item, id: String(idx), created_at: new Date().toISOString() } : item;
                      return (
                        <div key={idx} onClick={() => setSelectedAsset({ item: itemObj as GalleryItem, index: idx })} className="group aspect-square rounded-[40px] border-8 border-white overflow-hidden transition-all duration-500 relative cursor-pointer shadow-sm hover:shadow-2xl hover:scale-105">
                           <img src={itemObj.url} alt="Asset" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                           {(itemObj as GalleryItem).dna_prompt && (
                             <div className="absolute top-4 right-4 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white shadow-lg animate-pulse">
                                <Sparkles size={14} />
                             </div>
                           )}
                           <div className="absolute inset-0 bg-indigo-900/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-6">
                              <span className="bg-white/90 backdrop-blur text-[10px] text-indigo-900 px-3 py-1.5 rounded-full font-black tracking-widest">DNA READY</span>
                           </div>
                        </div>
                      );
                   })}
                </div>
             </div>
          </div>

        </div>
      </div>
    </div>
  );
}
