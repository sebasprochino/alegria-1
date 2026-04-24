import React, { useState } from 'react';
import { FlaskConical, Code2, Loader2, CheckCircle2, AlertCircle, Sparkles, Copy, Download } from 'lucide-react';

interface AnimaForgeUIProps {
  onBack?: () => void;
}

type GenerationState = 'idle' | 'generating' | 'done' | 'error';

export default function AnimaForgeUI({ onBack }: AnimaForgeUIProps) {
  const [description, setDescription] = useState('');
  const [state, setState] = useState<GenerationState>('idle');
  const [result, setResult] = useState<string | null>(null);

  const EXAMPLES = [
    'Dashboard con React, Recharts y Tailwind para analytics',
    'Landing page minimalista para una app de productividad',
    'Panel de administración con tabla de usuarios y gráficas',
    'Componente de chat en tiempo real con WebSockets',
  ];

  const handleGenerate = async () => {
    if (!description.trim()) return;
    setState('generating');
    setResult(null);

    try {
      const res = await fetch('/api/anima/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: `Actúa como Anima Forge. Genera el código completo de un proyecto real basado en: "${description}". Devuelve código funcional y comentado.`,
          provider: 'cascada',
        }),
      });

      if (!res.ok) throw new Error('Error en la generación');
      const data = await res.json();
      const content = data.response || data.content || data.result || 'Proyecto generado correctamente.';
      setResult(content);
      setState('done');
    } catch (e) {
      setState('error');
    }
  };

  const handleCopy = () => {
    if (result) navigator.clipboard.writeText(result);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] h-full overflow-hidden">
      {/* Header */}
      <div className="px-8 pt-8 pb-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <FlaskConical size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
              <span className="text-emerald-400 font-mono text-xl">&gt;_</span>
              Anima Forge
            </h1>
            <p className="text-[11px] text-slate-500 mt-0.5">Generador de Proyectos Reales</p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-2xl mx-auto px-6 py-8 space-y-6">

          {/* Textarea */}
          <div className="space-y-2">
            <label className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
              Describe tu aplicación
            </label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Ej: Dashboard con React, Recharts y Tailwind para analytics..."
              rows={5}
              className="w-full bg-[#161b22] border border-white/[0.08] rounded-2xl px-5 py-4 text-[14px] text-white placeholder-slate-600 outline-none focus:border-emerald-500/40 transition-colors resize-none font-light leading-relaxed"
            />
          </div>

          {/* Examples */}
          <div className="space-y-2">
            <p className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">Ejemplos rápidos</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLES.map(ex => (
                <button
                  key={ex}
                  onClick={() => setDescription(ex)}
                  className="text-[11px] px-3 py-1.5 bg-white/[0.04] border border-white/[0.06] rounded-xl text-slate-400 hover:text-emerald-400 hover:border-emerald-500/30 hover:bg-emerald-500/5 transition-all"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={!description.trim() || state === 'generating'}
            className={`w-full flex items-center justify-center gap-3 py-3.5 rounded-2xl text-[13px] font-black uppercase tracking-widest transition-all shadow-xl ${
              !description.trim() || state === 'generating'
                ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30'
            }`}
          >
            {state === 'generating' ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Generando Proyecto...
              </>
            ) : (
              <>
                <Code2 size={16} />
                Generar Proyecto Real
              </>
            )}
          </button>

          {/* Status indicators */}
          {state === 'error' && (
            <div className="flex items-center gap-2 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl">
              <AlertCircle size={14} className="text-red-400 flex-shrink-0" />
              <p className="text-[12px] text-red-400">
                Error al generar. Verifica que Anima esté conectada.
              </p>
            </div>
          )}

          {/* Result */}
          {state === 'done' && result && (
            <div className="space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={14} className="text-emerald-400" />
                  <span className="text-[11px] text-emerald-400 font-bold uppercase tracking-wider">
                    Proyecto generado
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-slate-400 hover:text-white transition-colors text-[11px] font-bold"
                    aria-label="Copiar código"
                  >
                    <Copy size={12} />
                    Copiar
                  </button>
                </div>
              </div>

              <pre className="bg-[#0d1117] border border-white/[0.08] rounded-2xl p-5 text-[12px] text-emerald-300 font-mono overflow-x-auto leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto custom-scrollbar">
                {result}
              </pre>
            </div>
          )}

          {/* Idle state hint */}
          {state === 'idle' && (
            <div className="flex flex-col items-center gap-3 py-8 text-center border border-dashed border-white/[0.06] rounded-2xl">
              <Sparkles className="text-emerald-500/30 w-8 h-8" />
              <p className="text-slate-600 text-[12px] max-w-xs">
                Describe tu aplicación arriba y Anima Forge generará el código funcional completo.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
