import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowRight, Mic, X } from 'lucide-react';

/**
 * ChatModuleMobile — Rediseño visual "Línea Silenciosa"
 * ---------------------------------------------------
 * Basado en el Manifiesto de Diseño Mobile de ALEGR-IA.
 * Estética: Objeto, no App. Niveles reducidos, tipografía aireada.
 */

export default function ChatModuleMobile({
  messages = [],
  onSend,
  onClose,
  isOpen = true,
}) {
  const [input, setInput]   = useState('');
  const [phase, setPhase]   = useState('closed');

  const timerRef  = useRef(null);
  const scrollRef = useRef(null);
  const inputRef  = useRef(null);

  // Máquina de estados para animaciones
  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    if (isOpen) {
      setPhase('opening');
      timerRef.current = setTimeout(() => setPhase('open'), 20);
    } else {
      setPhase('closing');
      timerRef.current = setTimeout(() => setPhase('closed'), 500);
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isOpen]);

  // Scroll inteligente
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
    if (nearBottom) {
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text) return;
    onSend?.(text);
    setInput('');
  }, [input, onSend]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const isVisible  = phase === 'open' || phase === 'opening';
  const isClosing  = phase === 'closing';
  const canInteract = isVisible && !isClosing;

  if (phase === 'closed') return null;

  // Estilos "Línea Silenciosa" — Basados en #F5F5F4
  const circleStyle = {
    position: 'fixed',
    borderRadius: '50%',
    backgroundColor: '#F5F5F4',
    transition: 'all 700ms cubic-bezier(0.23,1,0.32,1)',
    width:   canInteract ? '250vw' : '0rem',
    height:  canInteract ? '250vw' : '0rem',
    opacity: isVisible ? 1 : 0,
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    zIndex: 190
  };

  const containerStyle = {
    position: 'fixed',
    inset: 0,
    backgroundColor: '#F5F5F4',
    display: 'flex',
    flexDirection: 'column',
    transition: 'opacity 500ms ease-in-out',
    opacity: canInteract ? 1 : 0,
    pointerEvents: canInteract ? 'auto' : 'none',
    zIndex: 200,
  };

  return (
    <div role="dialog" aria-modal="true" className="font-sans antialiased">
      <div style={circleStyle} />

      <div style={containerStyle}>
        {/* HEADER — DIRECTO Y CHICO */}
        <div className="flex items-center justify-between px-4 py-3 shrink-0">
          <span className="text-[11px] tracking-[0.25em] uppercase text-neutral-400 font-light">
            Diálogo
          </span>
          <button 
            onClick={onClose}
            className="p-1 hover:opacity-60 transition-opacity"
          >
            <X size={18} className="text-neutral-400" />
          </button>
        </div>

        {/* MENSAJES — ESPACIADO Y LIMPIO */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-4 space-y-4 pb-28 custom-scrollbar-none"
        >
          {messages.map((msg, i) => {
            const text = msg.content ?? msg.text ?? '';
            const isUser = msg.role === 'user';

            return (
              <div 
                key={i} 
                className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                {isUser ? (
                  <div className="bg-black text-white rounded-2xl px-4 py-2 text-sm max-w-[80%] font-light tracking-tight shadow-sm">
                    {text}
                  </div>
                ) : (
                  <div className="text-neutral-600 text-[15px] px-2 max-w-[85%] font-light tracking-tight leading-relaxed">
                    {text}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* INPUT — EFECTO OBJETO VIDRIO */}
        <div className="absolute bottom-0 w-full px-4 pb-4 bg-gradient-to-t from-[#F5F5F4] via-[#F5F5F4] to-transparent">
          <div className="flex items-center gap-2 bg-white/80 backdrop-blur-md border border-black/5 rounded-full px-4 py-2 shadow-sm">
            <button type="button" className="text-neutral-300 hover:text-neutral-500 transition-colors">
              <Mic size={16} />
            </button>

            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribí o hablá..."
              className="flex-1 bg-transparent outline-none text-sm text-neutral-800 placeholder:text-neutral-300 font-light tracking-tight"
            />

            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className={`transition-all duration-300 ${
                input.trim() ? 'opacity-100 scale-100' : 'opacity-40 scale-95'
              }`}
            >
              <ArrowRight size={18} className="text-black" />
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
        .custom-scrollbar-none::-webkit-scrollbar {
          width: 0px;
          background: transparent;
        }
      `}</style>
    </div>
  );
}
