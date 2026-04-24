import React, { useState, useEffect } from 'react';
import { Menu, Globe, Mic, Send, Plus, X } from 'lucide-react';
import AlegrIAIcon from '../components/AlegrIAIcon';

/**
 * MandoUI: El Centro de Mandos Soberano de ALEGR-IA OS.
 * Implementa una estética minimalista, limpia y dinámica para la supervisión operativa.
 */
interface MandoUIProps {
  onBack: () => void;
  onSendMessage?: (message: string, metadata?: any) => void;
  onNavigate?: (targetId: string) => void;
}

export default function MandoUI({ onBack, onSendMessage, onNavigate }: MandoUIProps) {
  const [message, setMessage] = useState("");
  const [currentStatus, setCurrentStatus] = useState(0);

  // Estados dinámicos para el Centro de Mandos
  const statusMessages = [
    { main: "Hola, soy Anima,", sub: "tu inteligencia extendida." },
    { main: "Radar tiene novedades", sub: "sobre tu último proyecto." },
    { main: "Anima está lista,", sub: "esperando tu próxima idea." },
    { main: "Sincronizando contexto,", sub: "todo está en orden." }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStatus((prev) => (prev + 1) % statusMessages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleSend = () => {
    if (!message.trim() || !onSendMessage) return;
    onSendMessage(message);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="flex flex-col h-full bg-[#FDFDFD] text-[#1A1A1A] font-sans overflow-hidden animate-fade-in">
      
      {/* Contenido Principal */}
      <main className="flex-1 flex flex-col items-center justify-center px-8 text-center relative">
        
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-100/20 blur-[80px] rounded-full -z-10"></div>

        {/* Icono Central */}
        <div className="relative mb-12">
          <div className="absolute inset-0 bg-white blur-2xl rounded-full scale-150"></div>
          <div className="relative w-36 h-36 bg-white rounded-full flex items-center justify-center shadow-[0_8px_30px_rgb(0,0,0,0.02)] border border-white group transition-all duration-700 hover:shadow-2xl hover:scale-105">
            <AlegrIAIcon size={80} className="transition-transform duration-500" />
          </div>
        </div>

        {/* Texto de Bienvenida Dinámico */}
        <div className="h-32 flex flex-col justify-center">
            <div 
              key={currentStatus} 
              className="animate-in fade-in slide-in-from-bottom-4 duration-1000 space-y-2"
            >
              <h2 className="text-[34px] md:text-[42px] font-light leading-tight tracking-tight text-gray-800">
                {statusMessages[currentStatus].main.includes("Anima") ? (
                    <>
                    {statusMessages[currentStatus].main.split("Anima")[0]}
                    <span className="font-semibold text-black">Anima</span>
                    {statusMessages[currentStatus].main.split("Anima")[1]}
                    </>
                ) : (
                    statusMessages[currentStatus].main
                )}
              </h2>
              <h3 className="text-[24px] md:text-[30px] font-light text-gray-400 leading-tight">
                {statusMessages[currentStatus].sub}
              </h3>
            </div>
        </div>

        {/* Botones de Acción Rápida */}
        <div className="w-full max-w-[320px] space-y-4 mt-12">
          <button 
            onClick={() => onNavigate?.('anima_chat')}
            className="w-full py-4 bg-[#1E1E1E] text-white rounded-full flex items-center justify-center gap-3 font-medium hover:bg-black transition-all shadow-xl active:scale-95 shadow-black/10"
          >
            <div className="w-5 h-5 rounded-full border border-white/20 flex items-center justify-center">
              <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
            </div>
            Hablar
          </button>
          
          <button 
            onClick={() => onNavigate?.('noticias')}
            className="w-full py-4 bg-white text-gray-700 border border-gray-100 rounded-full flex items-center justify-center gap-3 font-medium hover:bg-gray-50 transition-all shadow-sm active:scale-95"
          >
            <Globe size={18} className="text-gray-400" />
            Explorar Mundo
          </button>
        </div>
      </main>

      {/* Área de Entrada Soberana */}
      <footer className="p-8 bg-white/90 backdrop-blur-xl border-t border-gray-100/50">
        <div className="max-w-3xl mx-auto flex flex-col gap-6">
          
          <p className="text-center text-gray-300 text-lg font-light tracking-wide italic">
            "Escribamos o creemos juntos"
          </p>

          <div className="flex items-center gap-3 bg-gray-50/50 p-2.5 rounded-[28px] border border-gray-100 shadow-inner group focus-within:border-purple-200 transition-all">
            <button 
              className="p-3 text-gray-400 hover:bg-white hover:text-gray-600 rounded-full transition-all shadow-sm"
              title="Adjuntar archivo o recurso"
              aria-label="Adjuntar archivo o recurso"
            >
              <Plus size={24} />
            </button>
            
            <div className="flex-1 relative flex items-center">
              <div className="flex items-center gap-1.5 bg-[#E8F0FE] text-[#1967D2] pl-3 pr-2 py-1.5 rounded-full text-[11px] font-bold mr-2 whitespace-nowrap border border-[#D2E3FC]">
                <span>CONTEXTO ACTIVO</span>
                <X 
                  size={14} 
                  className="cursor-pointer opacity-60 hover:opacity-100" 
                  aria-label="Eliminar contexto"
                  role="button"
                />
              </div>
              <input 
                type="text" 
                placeholder="Inicia un nuevo mandato..."
                className="w-full bg-transparent outline-none text-[18px] py-2 placeholder-gray-300 font-light"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
              />
            </div>

            <div className="flex items-center gap-2">
              <button 
                className="p-3 bg-white text-gray-400 rounded-full hover:shadow-md hover:text-gray-600 transition-all border border-gray-100"
                title="Entrada por voz"
                aria-label="Entrada por voz"
              >
                <Mic size={22} />
              </button>
              <button 
                onClick={handleSend}
                disabled={!message}
                title="Enviar mandato"
                aria-label="Enviar mandato"
                className={`p-3.5 rounded-full transition-all shadow-lg ${
                  message 
                    ? 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white shadow-purple-200 scale-100' 
                    : 'bg-gray-100 text-gray-300 shadow-none scale-95'
                }`}
              >
                <Send size={22} />
              </button>
            </div>
          </div>
        </div>
        <div className="h-4"></div>
      </footer>
    </div>
  );
}
