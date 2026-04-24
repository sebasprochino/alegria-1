import React, { useState, useRef } from 'react';
import { Sparkles, Send, Mic, Paperclip, Shield, X } from 'lucide-react';
import AlegrIAIcon from '../components/AlegrIAIcon';

/**
 * GenesisUI: El entorno de gestación conceptual de ALEGR-IA OS.
 * Enfocado en la "siembra" de ideas y el análisis visual de referencias.
 */
interface GenesisUIProps {
  onBack: () => void;
  onSendMessage?: (message: string, metadata?: any) => void;
}

export default function GenesisUI({ onBack, onSendMessage }: GenesisUIProps) {
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSend = () => {
    if ((!input.trim() && !selectedFile) || !onSendMessage) return;
    
    let metadata = null;
    if (selectedFile && previewUrl) {
      metadata = {
        name: selectedFile.name,
        type: selectedFile.type,
        data: previewUrl // base64
      };
    }

    onSendMessage(input || "[Análisis Visual Requerido]", metadata);
    setInput('');
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden wa-background animate-fade-in relative">
      {/* Glow Ambientales */}
      <div className="absolute top-1/4 -right-20 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 -left-20 w-80 h-80 bg-blue-600/5 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12 relative z-10">
        <div className="max-w-4xl w-full flex flex-col items-center">
          
          <div className="relative mb-8 group">
            <div className="absolute inset-0 bg-purple-500/20 blur-2xl rounded-full group-hover:bg-purple-500/30 transition-all duration-700"></div>
            <AlegrIAIcon size={100} className="relative z-10" />
          </div>
          
          <h2 className="text-5xl font-black text-white mb-2 tracking-tighter uppercase">Génesis</h2>
          <p className="text-slate-500 uppercase tracking-[0.4em] text-[10px] font-bold mb-12">Gestación de Universos y Semillas Conceptuales</p>

          <div className="w-full relative group max-w-2xl">
             {/* Central Hub de Entrada */}
             <div className="bg-[#1f2c34]/80 backdrop-blur-3xl border border-white/10 rounded-[40px] p-8 min-h-[320px] flex flex-col items-center justify-center text-center shadow-2xl relative overflow-hidden transition-all duration-500 group-hover:border-white/20">
                 {previewUrl ? (
                   <div className="w-full h-full absolute inset-0 group/preview animate-fade-in">
                      <img src={previewUrl} alt="Preview" className="w-full h-full object-cover opacity-30 blur-[4px]" />
                      <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/40">
                         <div className="relative w-40 h-40 rounded-3xl border-2 border-purple-500/50 overflow-hidden shadow-[0_0_50px_rgba(168,85,247,0.3)]">
                            <img src={previewUrl} alt="Main Preview" className="w-full h-full object-cover" />
                            <button 
                              onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                              title="Cerrar previsualización"
                              aria-label="Cerrar previsualización"
                              className="absolute top-2 right-2 p-1.5 bg-red-500/80 backdrop-blur-md rounded-full text-white hover:bg-red-600 transition-colors"
                            >
                               <X size={14} />
                            </button>
                         </div>
                         <p className="text-white text-sm mt-6 font-bold tracking-widest uppercase">Semilla Visual Detectada</p>
                      </div>
                   </div>
                 ) : (
                   <div className="animate-in fade-in zoom-in duration-700">
                      <div className="w-20 h-20 bg-white/5 rounded-[30px] flex items-center justify-center mb-8 border border-white/10 shadow-inner group-hover:scale-110 transition-transform duration-500">
                         <Sparkles className="text-purple-400 w-10 h-10 animate-pulse" />
                      </div>
                      <p className="text-gray-300 text-xl font-light tracking-tight mb-3">¿Qué universo vamos a gestar hoy?</p>
                      <span className="text-[10px] text-gray-600 uppercase tracking-[0.3em] font-mono italic">Protocolo de Semilla Activo // ACSP 4.0</span>
                   </div>
                 )}
             </div>

             {/* Input Bar Estilo Captura */}
             <div className="mt-10 flex flex-col gap-6">
                <div className="flex items-center gap-4 bg-[#1f2c34] border border-white/10 rounded-[24px] p-3 pr-5 group-focus-within:border-purple-500/50 transition-all shadow-2xl">
                    <input 
                      type="file" 
                      className="hidden" 
                      ref={fileInputRef} 
                      accept="image/*" 
                      onChange={handleFileChange} 
                      title="Seleccionar archivo"
                      aria-label="Seleccionar archivo"
                    />
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      aria-label="Adjuntar referencia visual"
                      title="Adjuntar referencia visual"
                      className={`p-3 rounded-full transition-all ${selectedFile ? 'bg-purple-500/20 text-purple-400' : 'text-gray-500 hover:text-white hover:bg-white/5'}`}
                    >
                       <Paperclip size={22} />
                    </button>
                    <input 
                       aria-label="Input de gestación"
                       value={input}
                       onChange={(e) => setInput(e.target.value)}
                       onKeyDown={handleKeyDown}
                       placeholder={selectedFile ? "Define el propósito de esta semilla..." : "Escribe el núcleo de tu idea..."}
                       className="flex-1 bg-transparent border-none outline-none text-white text-[17px] placeholder-gray-600 font-light"
                    />
                    <div className="flex items-center gap-2">
                       <button 
                         className="p-3 text-gray-500 hover:text-white transition-colors"
                         title="Entrada por voz"
                         aria-label="Entrada por voz"
                       >
                         <Mic size={22} />
                       </button>
                       <button 
                         onClick={handleSend}
                         aria-label="Iniciar gestación"
                         title="Iniciar gestación"
                         className={`p-3.5 rounded-2xl transition-all shadow-lg ${
                            (input.trim() || selectedFile) 
                              ? 'bg-purple-600 text-white shadow-purple-600/20 hover:bg-purple-500 scale-100' 
                              : 'bg-gray-800 text-gray-500 scale-95 opacity-50'
                         }`}
                       >
                          <Send size={20} />
                       </button>
                    </div>
                </div>
                
                <div className="flex justify-center gap-6">
                   <div className="flex items-center gap-2 text-[10px] font-bold text-gray-600 uppercase tracking-[0.2em]">
                      <Shield size={12} className="text-purple-500/40" />
                      Soberanía Asegurada
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
