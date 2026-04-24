import React, { useState, useRef } from 'react';
import {
  PenTool, Layers, Globe, Instagram, Linkedin, Twitter, Mail,
  RefreshCw, Shield, Copy, Check, ChevronRight, Sparkles,
  AlertTriangle, Loader
} from 'lucide-react';

interface ContentMachineUIProps {
  onBack?: () => void;
}

const DEFAULT_BRAND = {
  voice: 'Innovadora, accesible, inspiradora',
  mood: 'Energético y confiable',
};

async function callGenerate(params: {
  strategy: string;
  format: string;
  topic: string;
  mode?: string;
}): Promise<string> {
  const res = await fetch('/api/anima/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      strategy: params.strategy,
      format: params.format,
      topic: params.topic,
      mode: params.mode ?? 'generate',
      brand_voice: DEFAULT_BRAND.voice,
      brand_mood: DEFAULT_BRAND.mood,
    }),
  });
  if (!res.ok) throw new Error(`Backend ${res.status}`);
  const data = await res.json();
  if (data.status === 'error') throw new Error(data.message ?? 'Error desconocido');
  return data.response ?? '';
}

const ZapIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

export default function ContentMachineUI({ onBack }: ContentMachineUIProps) {
  const [strategy, setStrategy] = useState<'standard' | 'nexus' | 'radar'>('standard');
  const [format, setFormat] = useState<'instagram' | 'linkedin' | 'twitter' | 'newsletter'>('instagram');
  const [topic, setTopic] = useState('');
  const [ideas, setIdeas] = useState<string[]>([]);
  const [loadingIdeas, setLoadingIdeas] = useState(false);
  const [output, setOutput] = useState('');
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleIdeas = async () => {
    setLoadingIdeas(true);
    setError('');
    setIdeas([]);
    try {
      const raw = await callGenerate({ strategy, format, topic: '', mode: 'ideas' });
      const clean = raw.replace(/```json|```/g, '').trim();
      const parsed = JSON.parse(clean);
      setIdeas(Array.isArray(parsed) ? parsed : []);
    } catch (e: any) {
      setError(`No se pudieron generar ideas: ${e.message}`);
    } finally {
      setLoadingIdeas(false);
    }
  };

  const handleGenerate = async () => {
    if (!topic.trim()) { textareaRef.current?.focus(); return; }
    setGenerating(true);
    setOutput('');
    setError('');
    try {
      const result = await callGenerate({ strategy, format, topic: topic.trim() });
      setOutput(result);
    } catch (e: any) {
      setError(`Error al generar: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const strategies = [
    { id: 'standard', name: 'Estándar', desc: 'Brand Voice activa. Rápido y preciso.', icon: <ZapIcon size={16} /> },
    { id: 'nexus', name: 'Nexus (Deep Dive)', desc: 'Hechos profundos y conexiones ocultas.', icon: <Layers size={16} /> },
    { id: 'radar', name: 'Radar (Trends)', desc: 'Tendencias virales del momento.', icon: <Globe size={16} /> },
  ];

  const formats = [
    { id: 'instagram', name: 'Post Instagram', icon: <Instagram size={15} /> },
    { id: 'linkedin', name: 'Artículo LinkedIn', icon: <Linkedin size={15} /> },
    { id: 'twitter', name: 'Hilo Viral (X)', icon: <Twitter size={15} /> },
    { id: 'newsletter', name: 'Newsletter', icon: <Mail size={15} /> },
  ];

  const formatLabels: Record<string, string> = {
    instagram: 'Instagram', linkedin: 'LinkedIn', twitter: 'X / Twitter', newsletter: 'Newsletter',
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden animate-fade-in">
      <div className="flex-1 overflow-y-auto custom-scrollbar p-8">

        <div className="flex flex-col items-center mb-10">
          <div className="w-16 h-16 bg-purple-600 rounded-3xl flex items-center justify-center mb-6 shadow-2xl shadow-purple-600/20">
            <PenTool className="text-white w-8 h-8" />
          </div>
          <h2 className="text-4xl font-display font-bold text-white tracking-tighter mb-2">Content Machine AI</h2>
          <p className="text-xs text-gray-500 font-medium tracking-tight">
            Operando bajo: <span className="text-purple-400 font-bold uppercase tracking-widest">ALEGR-IA OS · Motor Central</span>
          </p>
        </div>

        <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-10">

          <div className="space-y-8">

            {/* 1. Estrategia */}
            <div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest font-mono block mb-3">1. ESTRATEGIA DE INTELIGENCIA</span>
              <div className="space-y-2">
                {strategies.map(opt => (
                  <div
                    key={opt.id}
                    onClick={() => { setStrategy(opt.id as any); setIdeas([]); }}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-center gap-4 ${
                      strategy === opt.id ? 'bg-purple-600/10 border-purple-500/50' : 'bg-[#1f2c34]/50 border-white/5 hover:bg-white/5'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${strategy === opt.id ? 'bg-purple-600 text-white' : 'bg-white/5 text-gray-500'}`}>
                      {opt.icon}
                    </div>
                    <div className="flex-1">
                      <h4 className={`text-[13px] font-bold ${strategy === opt.id ? 'text-white' : 'text-gray-300'}`}>{opt.name}</h4>
                      <p className="text-[10px] text-gray-500">{opt.desc}</p>
                    </div>
                    {strategy === opt.id && <ChevronRight size={14} className="text-purple-400" />}
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Formato */}
            <div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest font-mono block mb-3">2. FORMATO DE SALIDA</span>
              <div className="grid grid-cols-2 gap-3">
                {formats.map(opt => (
                  <button
                    key={opt.id}
                    onClick={() => setFormat(opt.id as any)}
                    className={`p-4 rounded-2xl border transition-all flex items-center gap-3 ${
                      format === opt.id ? 'bg-purple-600 border-purple-500 shadow-lg shadow-purple-600/20' : 'bg-[#1f2c34] border-white/5 hover:bg-white/5'
                    }`}
                  >
                    <div className={format === opt.id ? 'text-white' : 'text-gray-400'}>{opt.icon}</div>
                    <span className={`text-[11px] font-bold uppercase tracking-tight ${format === opt.id ? 'text-white' : 'text-gray-400'}`}>{opt.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* 3. Tema */}
            <div className="pt-4 border-t border-white/5">
              <div className="flex justify-between items-center mb-3">
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest font-mono">3. ¿DE QUÉ QUERÉS HABLAR?</span>
                <button
                  onClick={handleIdeas}
                  disabled={loadingIdeas}
                  className="flex items-center gap-1.5 text-[9px] font-bold text-purple-400 uppercase tracking-widest hover:text-purple-300 transition-colors disabled:opacity-40"
                >
                  {loadingIdeas ? <Loader size={12} className="animate-spin" /> : <RefreshCw size={12} />}
                  Nuevas ideas
                </button>
              </div>

              <textarea
                ref={textareaRef}
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="Escribí tu tema o elegí una idea abajo..."
                rows={3}
                className="w-full bg-[#1f2c34] border border-white/5 rounded-2xl p-4 text-[13px] text-white placeholder-gray-600 resize-none outline-none focus:border-purple-500/50 transition-colors font-mono leading-relaxed"
              />

              {ideas.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {ideas.map((idea, i) => (
                    <button
                      key={i}
                      onClick={() => setTopic(idea)}
                      className="text-[10px] bg-[#1f2c34] border border-purple-500/20 text-purple-300 rounded-xl px-3 py-1.5 hover:bg-purple-600/10 hover:border-purple-500/40 transition-all text-left leading-snug"
                    >
                      {idea}
                    </button>
                  ))}
                </div>
              )}

              {error && (
                <div className="mt-3 flex items-start gap-2 bg-red-500/5 border border-red-500/10 rounded-xl p-3">
                  <AlertTriangle size={13} className="text-red-400 mt-0.5 shrink-0" />
                  <span className="text-[10px] text-red-400/80 font-mono">{error}</span>
                </div>
              )}

              <button
                onClick={handleGenerate}
                disabled={generating || !topic.trim()}
                className="mt-4 w-full py-4 rounded-2xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 font-bold text-white text-sm shadow-lg shadow-purple-600/20"
              >
                {generating
                  ? <><Loader size={16} className="animate-spin" /> Generando con IA Híbrida…</>
                  : <><Sparkles size={16} /> Generar {formatLabels[format]}</>
                }
              </button>
            </div>
          </div>

          {/* Output Hub */}
          <div className="flex flex-col min-h-[500px]">
            <div className="flex-1 bg-[#1f2c34]/20 border border-white/5 rounded-[32px] flex flex-col overflow-hidden">

              {!output && !generating && (
                <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
                  <div className="w-20 h-20 bg-purple-600/10 rounded-full flex items-center justify-center mb-6 border border-purple-500/20">
                    <Sparkles size={36} className="text-purple-400/40" />
                  </div>
                  <h3 className="text-base font-bold text-white/40 mb-2">Output Hub</h3>
                  <p className="text-[10px] text-gray-700 uppercase tracking-widest leading-relaxed max-w-[200px]">
                    Configurá estrategia, formato y tema — el Motor Central hace el resto.
                  </p>
                </div>
              )}

              {generating && (
                <div className="flex-1 flex flex-col items-center justify-center p-12 gap-4">
                  <div className="relative">
                    <div className="w-16 h-16 rounded-full border-2 border-purple-600/20 border-t-purple-500 animate-spin" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <PenTool size={18} className="text-purple-400" />
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-[11px] font-bold text-purple-300 uppercase tracking-widest">Motor Central activo</p>
                    <p className="text-[10px] text-gray-600 mt-1">
                      {strategies.find(s => s.id === strategy)?.name} · {formatLabels[format]}
                    </p>
                  </div>
                </div>
              )}

              {output && !generating && (
                <div className="flex flex-col h-full">
                  <div className="flex items-center justify-between px-5 py-3 border-b border-white/5 shrink-0">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                        {formatLabels[format]} · {strategies.find(s => s.id === strategy)?.name}
                      </span>
                    </div>
                    <button onClick={handleCopy} className="flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-widest transition-colors text-gray-500 hover:text-white">
                      {copied
                        ? <><Check size={12} className="text-green-400" /><span className="text-green-400">Copiado</span></>
                        : <><Copy size={12} />Copiar</>}
                    </button>
                  </div>
                  <div className="flex-1 overflow-y-auto custom-scrollbar p-5">
                    <pre className="text-[12px] text-gray-200 whitespace-pre-wrap leading-relaxed font-mono">{output}</pre>
                  </div>
                  <div className="px-5 py-3 border-t border-white/5 flex items-center gap-2 shrink-0">
                    <Shield size={11} className="text-purple-500" />
                    <span className="text-[9px] font-bold text-gray-600 uppercase tracking-widest">
                      Generado bajo soberanía ALEGR-IA · Autoría humana preservada
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
