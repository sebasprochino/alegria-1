import { useEffect, useRef, useState, useCallback } from "react";
import { Sparkles, Cpu, Shield, Search as SearchIcon, Globe, MessageSquare, Youtube, ExternalLink, RotateCw, ArrowLeft as BackIcon, Volume2, VolumeX, Pause, Play, Square, X } from "lucide-react";
import { Analysis, SmokeSpan, Option } from "../utils/messageAdapter";

// Declaración de tipos para SpeechRecognition (Web Speech API)
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

interface SpeechRecognitionConstructor {
  new(): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor;
    webkitSpeechRecognition: SpeechRecognitionConstructor;
  }
}

// Represents one step in the pipeline execution trace
type TraceStep = {
  step: string;
  data: unknown;
};

type Message = {
  role: "user" | "anima";
  content: any;
  type?: "llm" | "tool" | "strategy" | "system" | "text" | "audio" | "video" | "file" | "youtube" | "web" | "image" | "options" | "decision" | "error" | "insight";
  url?: string;
  fileName?: string;
  duration?: number;
  options?: Option[];
  isRejected?: boolean;
  raw?: string;         // RAW Inspector — flattened
  analysis?: Analysis; // RAW Inspector — flattened
  rawAttempt?: string; // compat legacy
  alertLevel?: "none" | "warning" | "critical"; // Nivel de alerta pasiva
  trace?: TraceStep[];  // Pipeline execution trace (multi-step audit log)
  mode?: string;        // conversation, intention, execution
  source?: string;      // tool, llm, kernel
  originType?: string;  // type from backend
  intentionId?: string; // intention reference
  meta?: any;           // ACSP object envelope
  insight?: any;        // Detective analysis results
};

interface Props {
  messages: Message[];
  agent?: any; // Agregado para compatibilidad con App.jsx
  onSendMessage?: (message: string) => void; // Callback para enviar mensajes
  onExecuteOption?: (optionId: string | any, intentionId?: string) => void; // Callback para ejecutar una opción (ACSP)
  onOpenBrowser?: (title: string, url: string) => void; // Abrir ventana de navegación global
  onBack?: () => void; // Volver atrás (Móvil)
}

interface WebPage {
  url: string;
  visits: number;
}

// ───────────────────────────────────────────────────────────────────────────────
// DEBUGGER DE LENGUAJE — Resaltado inline de humo
// Convierte texto plano + smoke_spans en un array de elementos React
// con cada fragmento peligroso marcado en su color semántico.
//
// Colores:
//   emotional  → 🔴 rojo   (bg-red-500/20  text-red-300)
//   authority  → 🟡 amarillo (bg-yellow-500/20 text-yellow-300)
//   meta       → 🟣 violeta (bg-purple-500/20 text-purple-300)
// ───────────────────────────────────────────────────────────────────────────────
// SUB-COMPONENTE: Badge de Humo con Explainer (Tooltip)
// Muestra el criterio del Kernel sobre un fragmento específico.
// ───────────────────────────────────────────────────────────────────────────────
function SmokeSpanBadge({ text, span }: { text: string; span: SmokeSpan }) {
  const SPAN_COLORS: Record<string, string> = {
    emotional: "bg-red-500/20 text-white",
    authority: "bg-yellow-500/20 text-white",
    meta:      "bg-purple-500/20 text-white",
  };

  const colorClass = SPAN_COLORS[span.type] ?? "bg-zinc-500/20 text-zinc-300";

  return (
    <span className="relative group inline cursor-help">
      <mark className={`${colorClass} px-0.5 rounded transition-all group-hover:bg-opacity-40`}>
        {text}
      </mark>
      
      {/* Tooltip — Revelación de Criterio */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-[100] w-64 pointer-events-none transition-all animate-in fade-in slide-in-from-bottom-1 duration-200">
        <div className="bg-zinc-950/95 border border-zinc-700/60 shadow-2xl rounded-lg p-3 backdrop-blur-xl">
           <div className="flex items-center justify-between mb-2 border-b border-zinc-800 pb-1.5">
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                  span.type === 'emotional' ? 'bg-red-500' :
                  span.type === 'authority' ? 'bg-yellow-500' : 'bg-purple-500'
                }`}></span>
                <span className="text-[8px] font-bold uppercase tracking-[0.2em] text-zinc-500">Kernel Audit</span>
              </div>
              <span className="text-[7px] font-mono text-zinc-600 uppercase">ACSP-LOG</span>
           </div>
           
           <p className="text-[11px] text-zinc-200 leading-snug font-medium mb-2.5">
             {span.reason}
           </p>

           <div className="flex flex-col gap-1 text-[8px] font-mono border-t border-zinc-800/50 pt-1.5">
             <div className="flex justify-between">
               <span className="text-zinc-500 uppercase">Clase</span>
               <span className="text-zinc-400 capitalize">{span.type}</span>
             </div>
             <div className="flex justify-between">
               <span className="text-zinc-500 uppercase">Pattern</span>
               <span className="text-zinc-400">&ldquo;{span.pattern}&rdquo;</span>
             </div>
           </div>
        </div>
        {/* Flechita decorativa */}
        <div className="w-2 h-2 bg-zinc-950 border-r border-b border-zinc-700/60 rotate-45 absolute -bottom-1 left-1/2 -translate-x-1/2"></div>
      </div>
    </span>
  );
}

function renderHighlightedText(
  text: string,
  spans: SmokeSpan[]
): React.ReactNode[] {
  if (!text) return [];
  if (!spans || spans.length === 0) return [<span key="all">{text}</span>];

  const elements: React.ReactNode[] = [];
  let lastIndex = 0;

  // Renderéamos intercalando texto limpio y spans marcados
  for (let i = 0; i < spans.length; i++) {
    const span = spans[i];

    // Texto limpio anterior al span
    if (span.start > lastIndex) {
      elements.push(
        <span key={`txt-${i}`}>{text.slice(lastIndex, span.start)}</span>
      );
    }

    // Fragmento marcado con Tooltip interactivo
    elements.push(
      <SmokeSpanBadge 
        key={`mark-${i}`}
        text={text.slice(span.start, span.end)}
        span={span}
      />
    );

    lastIndex = span.end;
  }

  // Texto restante tras el último span
  if (lastIndex < text.length) {
    elements.push(<span key="tail">{text.slice(lastIndex)}</span>);
  }

  return elements;
}

// ───────────────────────────────────────────────────────────────────────────────
// OS UI COMPONENTS (Type-based)
// ───────────────────────────────────────────────────────────────────────────────

const LLMMessage = ({ content, role, formatTime, spans }: any) => {
  const isRejected = typeof content === 'string' && content.includes("🔴 Omitido");
  return (
  <div className={`flex items-end gap-2 ${role === "user" ? "flex-row-reverse" : "justify-start"} w-full mb-6`}>
    <div className={`w-8 h-8 rounded-full flex items-center justify-center border shadow-glow-xs flex-shrink-0 ${
      role === "user" 
        ? "bg-blue-500/10 text-blue-400 border-blue-500/20" 
        : isRejected ? "bg-red-500/10 text-red-400 border-red-500/20" : "bg-purple-500/10 text-purple-400 border-purple-500/20"
    }`}>
      {role === "user" ? "U" : <Sparkles size={16} />}
    </div>
    <div className={`relative max-w-[85%] md:max-w-[75%] px-4 py-3 rounded-2xl shadow-md border backdrop-blur-md ${
      role === "user"
        ? "rounded-br-none bg-blue-500/10 border-blue-500/20"
        : isRejected ? "rounded-bl-none bg-red-950/20 border-red-500/30" : "rounded-bl-none bg-[#1f2c34]/80 border-white/5"
    }`}>
      <div className={`text-[13px] leading-relaxed font-sans ${isRejected ? 'text-red-200' : role === 'user' ? 'text-slate-800 font-medium' : 'text-white/90'}`}>
        {spans && spans.length > 0 ? renderHighlightedText(content, spans) : content}
      </div>
      <div className={`flex items-center gap-1 justify-end mt-2 text-[9px] font-mono opacity-50 ${role === 'user' ? 'text-slate-500' : 'text-white'}`}>
        <span>{formatTime()}</span>
        {role === "anima" && <Shield size={8} className={isRejected ? "text-red-500" : "text-blue-500"} />}
      </div>
    </div>
  </div>
  );
};

const ToolMessage = ({ content, meta }: any) => {
  const isObject = typeof content === 'object' && content !== null;
  const isArray = Array.isArray(content);
  return (
    <div className="w-full bg-black/80 border border-emerald-500/30 rounded-lg p-4 mt-2 mb-6 shadow-[0_4px_24px_rgba(16,185,129,0.1)]">
      <div className="flex items-center gap-1.5 text-[9px] text-emerald-400/80 mb-3 border-b border-emerald-500/10 pb-2">
        <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
        <span className="font-mono tracking-[0.2em] uppercase">{meta?.source || "System Tool Render"}</span>
      </div>
      <div className="text-sm text-white space-y-2 overflow-x-auto">
        {!isObject ? (
           <pre className="font-mono text-[11px] text-zinc-300 whitespace-pre-wrap">{content}</pre>
        ) : isArray ? (
            content.map((item: any, i: number) => (
              <div key={i} className="border-b border-neutral-800 pb-2 mb-2 last:border-0 hover:bg-white/5 p-2 rounded transition">
                {item.title && <div className="font-bold text-emerald-300 text-[13px]">{item.title}</div>}
                {item.snippet && <div className="text-neutral-400 text-xs mt-1 leading-relaxed">{item.snippet}</div>}
              </div>
            ))
        ) : (
           <pre className="font-mono text-[11px] text-zinc-300 whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>
        )}
      </div>
    </div>
  );
};

const ContextualMemoryTimeline = ({ insight }: { insight: any }) => {
  const [isOpen, setIsOpen] = useState(false);
  if (!insight) return null;

  return (
    <div className="w-full mt-2 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 rounded-full text-[9px] font-bold text-blue-400 uppercase tracking-widest transition-all mb-2 ml-10"
      >
        <Cpu size={10} className={isOpen ? 'animate-spin-slow' : ''} />
        {isOpen ? 'Ocultar proceso de memoria' : 'Ver proceso de memoria'}
      </button>

      {isOpen && (
        <div className="ml-10 bg-slate-900/90 border border-blue-500/20 rounded-2xl p-6 relative overflow-hidden shadow-2xl backdrop-blur-xl">
          {/* Blueprint Grid Background */}
          <div className="absolute inset-0 opacity-[0.03] pointer-events-none blueprint-grid"></div>
          
          <div className="relative z-10 flex flex-col gap-8">
            {/* Stage 1: Auditoría */}
            <div className="flex gap-4 relative">
              <div className="absolute left-[15px] top-8 bottom-[-32px] w-[2px] bg-gradient-to-b from-blue-500/40 to-transparent dashed-line"></div>
              <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/40 flex items-center justify-center text-blue-400 shrink-0">
                <SearchIcon size={14} />
              </div>
              <div>
                 <h4 className="text-[10px] font-bold text-blue-300 uppercase tracking-[0.2em] mb-1">1. Auditoría de Conversaciones</h4>
                 <p className="text-xs text-slate-400 leading-relaxed max-w-sm">{insight.auditoria || "Analizando el flujo de conciencia anterior..."}</p>
              </div>
            </div>

            {/* Stage 2: Patrones */}
            <div className="flex gap-4 relative">
              <div className="absolute left-[15px] top-8 bottom-[-32px] w-[2px] bg-gradient-to-b from-blue-500/40 to-transparent dashed-line"></div>
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0">
                <Cpu size={14} />
              </div>
              <div>
                 <h4 className="text-[10px] font-bold text-indigo-300 uppercase tracking-[0.2em] mb-1">2. Extracción de Patrones</h4>
                 <div className="flex flex-wrap gap-2 mt-2">
                    {insight.patrones_identificados?.map((p: string, idx: number) => (
                      <span key={idx} className="bg-indigo-500/10 border border-indigo-500/20 text-[9px] text-indigo-200 px-2 py-0.5 rounded uppercase font-mono">{p}</span>
                    ))}
                 </div>
              </div>
            </div>

            {/* Stage 3: Resolución */}
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
                <Shield size={14} />
              </div>
              <div>
                 <h4 className="text-[10px] font-bold text-emerald-300 uppercase tracking-[0.2em] mb-1">3. Resolución Anticipada</h4>
                 <div className="space-y-3 mt-2">
                    {insight.estrategia_predictiva?.map((s: any, idx: number) => (
                      <div key={idx} className="bg-white/5 border border-white/5 p-3 rounded-xl hover:bg-white/10 transition-colors">
                        <div className="text-xs font-bold text-emerald-200 mb-1">{s.sugerencia}</div>
                        <div className="text-[10px] text-slate-500">{s.justificacion}</div>
                      </div>
                    ))}
                 </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
             <span className="text-[8px] font-mono text-slate-600 uppercase tracking-widest">Contextual Memory Nexus v2.6 // Secure Data Flow</span>
          </div>
        </div>
      )}
    </div>
  );
};

const StrategyMessage = ({ content, onExecuteOption, intentionId }: any) => (
  <div className="w-full mt-3 mb-6 space-y-3 bg-[#1f2c34]/50 border border-yellow-500/20 p-4 rounded-xl">
    <div className="text-[10px] font-bold tracking-[0.2em] uppercase text-yellow-500/80 mb-3 flex items-center gap-2">
      <Shield size={12} className="text-yellow-500" />
      Decisión Soberana Requerida
    </div>
    <div className="flex flex-col gap-2">
      {Array.isArray(content) && content.map((option: any) => (
        <button
          key={option.id}
          onClick={() => onExecuteOption?.(option.id, intentionId)}
          className="text-left px-4 py-3 bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-100/90 transition-all active:scale-[0.98]"
        >
          <div className="font-bold text-sm tracking-wide">{option.label}</div>
          {option.description && (
             <div className="text-[11px] opacity-70 mt-1 uppercase tracking-tight">{option.description}</div>
          )}
        </button>
      ))}
    </div>
  </div>
);

// ───────────────────────────────────────────────────────────────────────────────
// COMPONENTE: Consola de Auditoría Live con Timeline Engine (BUG-05 + Timeline)
// ───────────────────────────────────────────────────────────────────────────────
const RealTimeAuditLog = () => {
  const [timeline, setTimeline] = useState<Record<string, any>>({});
  const [isVisible, setIsVisible] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Normalizador de eventos (Timeline Engine)
  const reduceEvent = (state: any, event: any) => {
    const { intention_id, stage, timestamp, agent, data } = event;
    if (!intention_id) return state;

    if (!state[intention_id]) {
      state[intention_id] = {
        id: intention_id,
        agent: agent || "SYSTEM",
        start: timestamp,
        stages: {},
        lastUpdate: timestamp,
        alertLevel: "authorized" // Por defecto
      };
    }

    const entry = state[intention_id];
    entry.lastUpdate = timestamp;

    // Capturar nivel de alerta desde el stage 'guard'
    if (stage === "guard" && data?.alert_level) {
      entry.alertLevel = data.alert_level;
    }
    if (stage === "error") {
      entry.alertLevel = "rejected";
    }


    if (!entry.stages[stage]) {
      entry.stages[stage] = {
        start: timestamp,
        end: timestamp + (data?.duration || 0.05), // Estimación o real
        data: data
      };
    } else {
      entry.stages[stage].end = timestamp;
      if (data) entry.stages[stage].data = { ...entry.stages[stage].data, ...data };
    }

    return { ...state };
  };

  useEffect(() => {
    const evtSource = new EventSource("/api/anima/audit/stream");
    
    evtSource.onmessage = (event) => {
      try {
        if (event.data.startsWith(":")) return;
        const data = JSON.parse(event.data);
        setTimeline(prev => reduceEvent({ ...prev }, data));
      } catch (e) {
        console.error("Audit Parse Error", e);
      }
    };

    return () => evtSource.close();
  }, []);

  const loadAuditHistory = async (intentionId: string) => {
    try {
      const res = await fetch(`/api/anima/audit/history/${intentionId}`);
      const data = await res.json();
      if (data.events) {
        data.events.forEach((evt: any) => {
          setTimeline(prev => reduceEvent({ ...prev }, evt));
        });
      }
    } catch (e) {
      console.error("Failed to load audit history", e);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [timeline]);

  const TimelineItem = ({ item }: { item: any }) => {
    const stages = Object.entries(item.stages);
    const totalStart = item.start;
    const totalEnd = Math.max(...stages.map(([_, s]: any) => s.end || s.start));
    const totalDuration = totalEnd - totalStart || 0.1;

    const STAGE_COLORS: Record<string, string> = {
      received: "bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.5)]",
      provider: "bg-purple-400 shadow-[0_0_8px_rgba(192,132,252,0.5)]",
      response: "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]",
      guard:    "bg-zinc-400 shadow-[0_0_8px_rgba(255,255,255,0.2)]",
      antigravity: "bg-[#ff7b72] shadow-[0_0_8px_rgba(255,123,114,0.5)]",
      error:    "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]",
      memory:   "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.5)]",
      override: "bg-magenta-500 shadow-[0_0_12px_rgba(255,0,255,0.6)] animate-pulse"
    };

    const ALERT_COLORS: Record<string, string> = {
      authorized: "bg-emerald-500",
      doubt:      "bg-amber-500",
      rejected:   "bg-red-500"
    };

    const ALERT_GLOW: Record<string, string> = {
      authorized: "shadow-[0_0_10px_rgba(16,185,129,0.3)]",
      doubt:      "shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse",
      rejected:   "shadow-[0_0_20px_rgba(239,68,68,0.7)] animate-pulse"
    };

    // Sub-componente para evitar advertencias de estilos inline en el componente principal
    const DynamicSegment = ({ start, len, colorClass, label, alert }: any) => {
      return (
        <div 
          className={`h-full absolute transition-all duration-500 ${colorClass} timeline-segment`}
          style={{ '--segment-start': `${start}%`, '--segment-width': `${len}%` } as React.CSSProperties}
          title={`${label}: ${len.toFixed(2)}% | Alert: ${alert}`}
        />
      );
    };

    return (
      <div className="mb-4 group animate-in fade-in slide-in-from-left-2 duration-300">
        <div className="flex items-center justify-between mb-1.5 px-1">
          <div className="flex items-center gap-2">
             {/* Indicador de Status Semántico */}
             <div className={`w-2 h-2 rounded-full ${ALERT_COLORS[item.alertLevel]} ${ALERT_GLOW[item.alertLevel]}`}></div>
             <span className="text-[10px] font-black text-magenta-300 tracking-tighter">{item.agent}</span>
             <button 
               onClick={() => loadAuditHistory(item.id)}
               className="text-[8px] font-mono text-zinc-500 hover:text-magenta-400 transition-colors cursor-pointer"
               title="Cargar historial completo de esta intención (Replay)"
             >
               ID:{item.id.slice(0,8)}
             </button>
          </div>
          <span className="text-[9px] font-mono text-zinc-400">{(totalDuration).toFixed(2)}s</span>
        </div>

        {/* Track */}
        <div className="h-2.5 bg-zinc-900/80 rounded-full overflow-hidden border border-white/5 flex relative">
          {/* Capa de Alerta (Overlay semántico) */}
          {item.alertLevel !== "authorized" && (
            <div className={`absolute inset-0 opacity-20 pointer-events-none mix-blend-screen z-10 ${ALERT_COLORS[item.alertLevel]}`}></div>
          )}

          {stages.map(([name, s]: any) => {
            const startPct = ((s.start - totalStart) / totalDuration) * 100;
            const endPct = ((s.end - totalStart) / totalDuration) * 100;
            const width = Math.max(endPct - startPct, 3);

            return (
              <DynamicSegment 
                key={name}
                start={startPct}
                len={width}
                colorClass={STAGE_COLORS[name] || "bg-zinc-500"}
                label={name.toUpperCase()}
                alert={item.alertLevel}
              />
            );
          })}
        </div>

        {/* Firma Soberana (Trazabilidad Legal) */}
        {item.stages.override && (
          <div className="mt-1 px-1 flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-500">
            <div className="flex items-center gap-1">
              <div className="w-1 h-1 bg-magenta-500 rounded-full shadow-[0_0_4px_magenta]"></div>
              <span className="text-[7px] font-mono text-magenta-500/80 uppercase tracking-widest font-black">
                Acta: {item.stages.override.data?.signature || "PENDING"}
              </span>
            </div>
            <span className="text-[7px] font-mono text-zinc-500 italic">
              Verified by Sovereign Kernel
            </span>
          </div>
        )}
      </div>
    );
  };

  if (!isVisible) {
    return (
      <button 
        onClick={() => setIsVisible(true)}
        className="fixed bottom-24 right-6 z-[60] bg-[#0b141a]/90 border border-magenta-500/30 p-3 rounded-full text-magenta-400 hover:scale-110 transition-all shadow-[0_0_15px_rgba(255,0,255,0.2)] group"
        title="Ver Timeline de Auditoría Cognitiva"
        aria-label="Abrir Consola de Auditoría"
      >
        <RotateCw size={18} className="group-hover:rotate-180 transition-transform duration-500" />
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-magenta-500 rounded-full animate-ping"></div>
      </button>
    );
  }

  const sortedTimeline = Object.values(timeline)
    .sort((a, b) => a.start - b.start)
    .slice(-15);

  return (
    <div className="fixed bottom-24 right-6 z-[60] w-80 bg-[#0b141a]/95 border border-magenta-500/40 rounded-2xl shadow-2xl backdrop-blur-3xl overflow-hidden animate-in slide-in-from-right-8 duration-300">
      <div className="flex items-center justify-between px-4 py-3 bg-magenta-500/10 border-b border-magenta-500/20">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 bg-magenta-500 rounded-full animate-pulse shadow-[0_0_8px_magenta]"></div>
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-magenta-300">Cognitive Timeline</span>
        </div>
        <button 
          onClick={() => setIsVisible(false)} 
          className="text-zinc-500 hover:text-white transition-colors"
          title="Cerrar Consola"
          aria-label="Cerrar Consola de Auditoría"
        >
          <X size={14} />
        </button>
      </div>

      <div ref={scrollRef} className="h-80 overflow-y-auto p-4 custom-scrollbar bg-black/10">
        {sortedTimeline.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-zinc-600 italic gap-2 opacity-50">
            <Cpu size={24} className="animate-pulse" />
            <span className="text-[10px] uppercase tracking-widest">Sincronizando...</span>
          </div>
        )}
        {sortedTimeline.map(item => (
          <TimelineItem key={item.id} item={item} />
        ))}
      </div>
      
      <div className="px-4 py-2 bg-black/40 border-t border-white/5 flex justify-between items-center text-[7px] text-zinc-600 font-mono tracking-widest uppercase">
         <span>Real-time Telemetry Active</span>
         <span>SOTA v4.2</span>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────────────────
// COMPONENTE: Panel de Intervención Humana (Override) — ACSP Compliant
// ───────────────────────────────────────────────────────────────────────────────
const OverridePanel = ({ msg, onOverride }: { msg: any, onOverride: (action: string, content: string, intention_id?: string) => void }) => {
  // Solo mostramos si hay un bloqueo (Doubt o Rejected)
  const isBlocked = msg.status === "Doubt" || msg.status === "Rejected";
  if (!isBlocked) return null;

  const alertColors = {
    none: "border-emerald-500/50 bg-emerald-500/5 text-emerald-200",
    warning: "border-amber-500/50 bg-amber-500/5 text-amber-200",
    critical: "border-red-500/50 bg-red-500/5 text-red-200"
  };

  const colorClass = alertColors[msg.alertLevel as keyof typeof alertColors] || alertColors.warning;

  return (
    <div className={`mt-3 p-3 border rounded-xl animate-in zoom-in-95 duration-300 ${colorClass}`}>
      <div className="flex items-center gap-2 mb-3">
         <Shield size={14} className={msg.alertLevel === 'critical' ? 'text-red-500' : 'text-amber-500'} />
         <span className="text-[10px] font-bold uppercase tracking-widest">Contenido Restringido por el Kernel</span>
      </div>
      
      <p className="text-[11px] opacity-80 leading-relaxed mb-4">
        {msg.alertLevel === 'critical' 
          ? "La salida ha sido bloqueada por violaciones críticas de coherencia o límites éticos."
          : "El sistema detecta ambigüedad o ruido excesivo. Se requiere mandato manual para liberar."}
      </p>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onOverride("force_render", msg.blocked_response || msg.raw, msg.intentionId)}
          className="px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-[10px] font-bold uppercase tracking-tighter transition-all flex items-center gap-1.5"
          title="Liberar contenido original bajo responsabilidad del operador"
        >
          <Play size={10} /> Forzar Visualización
        </button>
        <button
          onClick={() => onOverride("retry_strict", msg.raw || msg.content, msg.intentionId)}
          className="px-3 py-1.5 bg-magenta-500/20 hover:bg-magenta-500/40 border border-magenta-500/30 rounded-lg text-[10px] font-bold uppercase tracking-tighter transition-all flex items-center gap-1.5"
          title="Solicitar regeneración con restricciones de coherencia máximas"
        >
          <RotateCw size={10} /> Reintentar Seguro
        </button>
      </div>
    </div>
  );
};

export default function AnimaUI({ messages, onSendMessage, onExecuteOption, onOpenBrowser, onBack }: Props) {
  const lastSpoken = useRef<string | null>(null);
  const [input, setInput] = useState("");
  const [suggestion, setSuggestion] = useState<{ name: string; url: string } | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const [inspecting, setInspecting] = useState(false);
  const [listening, setListening] = useState(false);
  const [openTrace, setOpenTrace] = useState<number | null>(null);
  const processedResultsRef = useRef<Set<number>>(new Set());
  const [webUrl, setWebUrl] = useState<string | null>(null);
  const [webTitle, setWebTitle] = useState("Explorador Soberano");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isVoicePaused, setIsVoicePaused] = useState(false);

  // Efecto para detectar navegación desde el backend
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    
    // Si el mensaje tiene un payload de navegación, abrimos la transposición web
    if (last.meta?.navPayload) {
      const payload = last.meta.navPayload;
      setWebUrl(payload.url);
      setWebTitle(payload.name || "Web");
      console.log("🚀 [SOVEREIGN NAV] Abriendo Ventana Flotante:", payload.url);
    }
  }, [messages]);

  // Diccionario dinámico de URLs con contador de visitas
  const [webDictionary, setWebDictionary] = useState<Record<string, WebPage>>(() => {
    try {
      const saved = localStorage.getItem("webDictionary");
      return saved
        ? JSON.parse(saved)
        : {
          youtube: { url: "https://www.youtube.com", visits: 0 },
          wikipedia: { url: "https://www.wikipedia.org", visits: 0 },
          google: { url: "https://www.google.com", visits: 0 },
        };
    } catch {
      return {
        youtube: { url: "https://www.youtube.com", visits: 0 },
        wikipedia: { url: "https://www.wikipedia.org", visits: 0 },
        google: { url: "https://www.google.com", visits: 0 },
      };
    }
  });

  // Guardar en localStorage al actualizar diccionario
  useEffect(() => {
    localStorage.setItem("webDictionary", JSON.stringify(webDictionary));
  }, [webDictionary]);

  // --- Text-to-Speech ---
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    if (last.role !== "anima") return;
    if (!last.content) return;
    if (lastSpoken.current === last.content) return;

    let texto = "";
    if (typeof last.content === "string") {
      texto = last.content.trim();
    } else if (last.type === "strategy") {
      texto = "Toma una decisión en la consola.";
    }

    if (!texto) return;
    lastSpoken.current = last.content; // Guardar la referencia al objeto u string para no repetir

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();

      const elegirVoz = () => {
        const voces = window.speechSynthesis.getVoices();
        return (
          voces.find(v => v.lang === "es-AR" && v.name.toLowerCase().includes("google")) ||
          voces.find(v => v.lang.startsWith("es")) ||
          voces[0]
        );
      };

      const hablar = () => {
        const voz = elegirVoz();
        if (!voz) return;

        const u = new SpeechSynthesisUtterance(texto);
        u.voice = voz;
        u.lang = "es-AR";
        u.rate = 0.95;
        u.pitch = 1.0;
        u.volume = 1;

        u.onstart = () => {
          setIsSpeaking(true);
          setIsVoicePaused(false);
        };
        u.onend = () => {
          setIsSpeaking(false);
          setIsVoicePaused(false);
        };
        u.onerror = () => {
          setIsSpeaking(false);
          setIsVoicePaused(false);
        };

        window.speechSynthesis.speak(u);
      };

      if (window.speechSynthesis.getVoices().length === 0) {
        window.speechSynthesis.onvoiceschanged = hablar;
      } else {
        hablar();
      }
    }
  }, [messages]);

  const toggleVoice = () => {
    if (!("speechSynthesis" in window)) return;

    if (isSpeaking) {
      if (isVoicePaused) {
        window.speechSynthesis.resume();
        setIsVoicePaused(false);
      } else {
        window.speechSynthesis.pause();
        setIsVoicePaused(true);
      }
    }
  };

  const stopVoice = () => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsVoicePaused(false);
  };

  // --- Función para enviar mensajes ---
  const handleSend = () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    // Primero intentar como comando de voz
    const isLocalCommand = handleVoiceCommand(trimmedInput);

    // Solo enviar al chat si no es un comando local
    if (!isLocalCommand && onSendMessage) {
      onSendMessage(trimmedInput);
    }

    setInput("");
  };

  // --- Abrir página web ---
  const openWebPage = (name: string) => {
    const page = webDictionary[name];
    if (!page) return;
    
    // Abrir directamente en el overlay flotante soberano
    setWebUrl(page.url);
    setWebTitle(name.toUpperCase());
    console.log(`🌐 [NAV] Abriendo ${name} → ${page.url}`);

    // Incrementar visitas
    setWebDictionary(prev => ({
      ...prev,
      [name]: { ...prev[name], visits: prev[name].visits + 1 },
    }));

    // Quitar sugerencia
    setSuggestion(null);
  };

  // --- Detectar sugerencias ---
  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    if (last.role !== "user") return;

    if (!last.content) return;
    const userText = last.content.toLowerCase();
    let bestMatch: { name: string; url: string; visits: number } | null = null;

    for (const key in webDictionary) {
      if (userText.includes(key)) {
        const page = webDictionary[key];
        if (!bestMatch || page.visits > bestMatch.visits) {
          bestMatch = { name: key, url: page.url, visits: page.visits };
        }
      }
    }

    if (bestMatch) {
      setSuggestion({ name: bestMatch.name, url: bestMatch.url });
    } else {
      setSuggestion(null);
    }
  }, [messages, webDictionary]);

  // --- Comandos de voz ---
  const handleVoiceCommand = useCallback((command: string): boolean => {
    const lower = command.toLowerCase();

    // Agregar página: "Agregar página: nombre con URL https://..."
    const addMatch = lower.match(/agregar página[:]? (\w+) con url (https?:\/\/\S+)/);
    if (addMatch) {
      const name = addMatch[1];
      const url = addMatch[2];
      setWebDictionary(prev => ({ ...prev, [name]: { url, visits: 0 } }));
      console.log(`Página agregada: ${name} → ${url}`);
      return true;
    }

    // Abrir página por voz
    for (const key in webDictionary) {
      if (lower.includes(`abrir ${key}`)) {
        openWebPage(key);
        console.log("Abrir página web:", webDictionary[key].url);
        return true;
      }
    }

    // Abrir URL directa: "Navegar a https://..."
    const navMatch = lower.match(/(?:navegar a|abrir url|visitar) (https?:\/\/\S+)/);
    if (navMatch) {
      const url = navMatch[1];
      setWebUrl(url);
      setWebTitle("Navegación Segura");
      console.log(`🌐 [NAV] Apertura directa → ${url}`);
      return true;
    }

    // Cerrar página
    if (lower.includes("cerrar página") || lower.includes("cerrar web")) {
      setWebUrl(null);
      setWebTitle("Explorador Soberano");
      console.log("🔒 [NAV] WebView cerrado por comando");
      return true;
    }

    console.log("Comando de voz general:", command);
    return false;
  }, [webDictionary]);

  // Usamos una referencia para evitar stale closures en el listener del micrófono
  const handleVoiceCommandRef = useRef(handleVoiceCommand);
  useEffect(() => {
    handleVoiceCommandRef.current = handleVoiceCommand;
  }, [handleVoiceCommand]);

  // --- Reconocimiento de voz ---
  useEffect(() => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) return;

    const SpeechRecognitionClass =
      (window as Window).SpeechRecognition || (window as Window).webkitSpeechRecognition;

    const recognition = new SpeechRecognitionClass();
    recognition.lang = "es-AR";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      // Evitar procesamiento duplicado del mismo evento/índice
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (!result.isFinal) continue;
        
        // Si ya procesamos este índice de resultado, ignorar
        if (processedResultsRef.current.has(i)) continue;
        processedResultsRef.current.add(i);

        const transcript = result[0].transcript.trim();
        if (!transcript) continue;

        console.log("🎙️ [VOICE] Detectado:", transcript);
        
        const isLocalCommand = handleVoiceCommandRef.current(transcript);
        if (!isLocalCommand && onSendMessage) {
          console.log("💬 [VOICE] Enviando a chat:", transcript);
          onSendMessage(transcript);
        }
      }
    };

    recognition.onerror = (e: SpeechRecognitionErrorEvent) => {
      console.error("Speech recognition error:", e);
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current = recognition;

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onSendMessage]); // Quitamos webDictionary y usamos la Ref para la lógica local

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  // Formatear hora para los mensajes
  const formatTime = () => {
    const now = new Date();
    return now.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
  };

  // Formatear duración de audio/video
  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Extraer ID de YouTube
  const getYouTubeId = (url: string) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)/);
    return match ? match[1] : null;
  };

  // Renderizar contenido del mensaje según tipo
  const InsightMessage = ({ insight }: { insight: any }) => {
    if (!insight) return null;
    return (
      <div className="w-full bg-purple-900/20 border border-purple-500/30 p-5 rounded-[24px] mt-4 animate-fade-in shadow-2xl shadow-purple-950/20 border-l-4 border-l-purple-500">
        <div className="flex items-center gap-2 text-[10px] text-purple-400 font-bold uppercase tracking-[0.2em] mb-4">
          <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse shadow-[0_0_10px_purple]"></span>
          Auditoría Cognitiva (Detective Contextual)
        </div>

        <div className="space-y-4">
          <div className="bg-black/20 p-3 rounded-xl border border-white/5">
            <span className="text-[9px] text-purple-300/50 uppercase font-black block mb-2 tracking-widest">Resumen Ejecutivo:</span>
            <p className="text-sm font-medium text-purple-50/90 leading-relaxed font-premium">{insight.auditoria}</p>
          </div>

          {insight.patrones_identificados?.length > 0 && (
            <div>
              <span className="text-[9px] text-purple-300/50 uppercase font-black block mb-2 tracking-widest">Patrones Detectados:</span>
              <div className="flex flex-wrap gap-2">
                {insight.patrones_identificados.map((p: string, i: number) => (
                  <span key={i} className="text-[10px] bg-purple-500/10 text-purple-300 px-3 py-1 rounded-lg border border-purple-500/20 font-bold">
                    #{p.toUpperCase()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderMessageContent = (msg: Message) => {
    // Si es un insight puro (no implementado así ahora, pero por si acaso)
    if (msg.type === "insight") return <InsightMessage insight={msg.insight} />;
    const messageType = msg.type || 'text';

    switch (messageType) {
      case 'audio':
        return (
          <div className="flex items-center gap-3 pr-12 min-w-[200px]">
            <button
              className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 hover:bg-emerald-600 transition-colors"
              aria-label="Reproducir audio"
              onClick={() => {
                const audio = document.getElementById(`audio-${msg.url}`) as HTMLAudioElement;
                if (audio) {
                  if (audio.paused) {
                    // Evitar interrupción de play() según mejores prácticas de Chrome
                    const playPromise = audio.play();
                    if (playPromise !== undefined) {
                      playPromise
                        .then(() => {
                           // Play started successfully
                        })
                        .catch((error) => {
                          if (error.name !== "AbortError") {
                             console.log("Audio play error:", error);
                          }
                        });
                    }
                  } else {
                    audio.pause();
                  }
                }
              }}

            >
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
            <div className="flex-1">
              <div className="h-1 bg-white/20 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-400 w-0" />
              </div>
              <div className="flex justify-between text-xs text-white/50 mt-1">
                <span>0:00</span>
                <span>{formatDuration(msg.duration)}</span>
              </div>
            </div>
            <audio id={`audio-${msg.url}`} src={msg.url} className="hidden" preload="metadata" />
          </div>
        );

      case 'video':
        return (
          <div className="pr-12">
            <video
              src={msg.url}
              controls
              className="rounded-lg max-w-full max-h-64"
              preload="metadata"
            >
              Tu navegador no soporta video.
            </video>
            {msg.content && (
              <p className="text-white text-sm mt-2">{msg.content}</p>
            )}
          </div>
        );

      case 'image':
        return (
          <div className="pr-12">
            <img
              src={msg.url}
              alt={msg.content || 'Imagen'}
              className="rounded-lg max-w-full max-h-64 cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => msg.url && window.open(msg.url, '_blank')}
            />
            {msg.content && (
              <p className="text-white text-sm mt-2">{msg.content}</p>
            )}
          </div>
        );

      case 'youtube':
        const youtubeId = msg.url ? getYouTubeId(msg.url) : null;
        return (
          <div className="pr-12">
            {youtubeId ? (
              <div className="relative rounded-lg overflow-hidden">
                <iframe
                  width="280"
                  height="158"
                  src={`https://www.youtube.com/embed/${youtubeId}`}
                  title="YouTube video"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="rounded-lg"
                />
              </div>
            ) : (
              <a
                href={msg.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-emerald-400 hover:underline"
              >
                <span className="text-2xl">▶️</span>
                <span>{msg.content || 'Ver en YouTube'}</span>
              </a>
            )}
            {msg.content && youtubeId && (
              <p className="text-white text-sm mt-2">{msg.content}</p>
            )}
          </div>
        );

      case 'file':
        return (
          <div className="pr-12">
            <a
              href={msg.url}
              download={msg.fileName}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors bg-white/5"
            >
              <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm truncate">{msg.fileName || 'Archivo'}</p>
                <p className="text-white/50 text-xs">{msg.content || 'Tocar para descargar'}</p>
              </div>
              <svg className="w-5 h-5 text-white/50" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" />
              </svg>
            </a>
          </div>
        );

      case 'web':
        return (
          <div className="pr-12">
            <a
              href={msg.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors bg-white/5"
            >
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <span className="text-xl">🌐</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm truncate">{msg.content || 'Enlace web'}</p>
                <p className="text-emerald-400 text-xs truncate">{msg.url}</p>
              </div>
              <svg className="w-5 h-5 text-white/50" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 19H5V5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" />
              </svg>
            </a>
          </div>
        );

      case 'decision':
        return (
          <div className="pr-12 space-y-3">
            <p className="text-white text-sm mb-3">La Operadora requiere tu decisión:</p>
            <div className="grid grid-cols-1 gap-2">
              {msg.options?.map(opt => (
                <button
                  key={opt.id}
                  onClick={() => onExecuteOption?.(opt.id, msg.intentionId)}
                  className="text-left px-4 py-2.5 bg-white/10 hover:bg-emerald-500/30 border border-white/20 hover:border-emerald-500/50 rounded-xl text-white text-sm transition-all active:scale-95"
                >
                  <div className="font-bold">{opt.label}</div>
                  <div className="text-[10px] opacity-60 uppercase tracking-tighter mt-0.5">{opt.description}</div>
                </button>
              ))}
            </div>

            {msg.rawAttempt && (
              <div className="mt-4 pt-4 border-t border-white/5">
                <details className="group">
                  <summary className="list-none cursor-pointer flex items-center gap-2 text-[10px] text-zinc-500 hover:text-zinc-300 transition-colors uppercase tracking-widest font-bold">
                    <div className="w-1.5 h-1.5 bg-zinc-600 rounded-full group-open:bg-amber-500 transition-colors"></div>
                    Inspeccionar Salida del Modelo
                  </summary>
                  <div className="mt-3 p-3 bg-black/40 rounded-xl border border-white/5 font-mono text-[10px] text-zinc-400 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                    <div className="mb-2 flex items-center gap-2 text-amber-500/80">
                      <span>⚠️ RUIDO DETECTADO / PROTOCOLO VIOLADO</span>
                    </div>
                    {msg.rawAttempt}
                  </div>
                </details>
              </div>
            )}
          </div>
        );

      case 'text':
      default: {
        // Los datos ya vienen normalizados por el messageAdapter en App.jsx
        const analysis     = msg.analysis ?? null;
        const spans        = analysis?.smoke_spans ?? [];
        const flags        = analysis?.flags ?? [];
        const smokeSignals = analysis?.smoke_signals ?? [];
        const confidence   = analysis?.confidence ?? 1.0;
        const types        = Array.isArray(analysis?.type) ? analysis.type : ["informational"];
        const parseMode    = analysis?.parse_mode ?? "";
        const rawText      = msg.raw ?? msg.rawAttempt ?? "";

        const confidencePct = Math.round(confidence * 100);
        const confidenceBarClass =
          confidence >= 0.8 ? "bg-emerald-500" :
          confidence >= 0.5 ? "bg-amber-500"   : "bg-red-500";
        const confidenceTextClass =
          confidence >= 0.8 ? "text-emerald-400" :
          confidence >= 0.5 ? "text-amber-400"   : "text-red-400";

        const typeBadgeClass =
          types.includes("informational") ? "bg-emerald-500/15 text-emerald-400" :
          types.includes("emotional")     ? "bg-red-500/15 text-red-400"         :
          types.includes("authority")     ? "bg-yellow-500/15 text-yellow-400"   :
                                            "bg-purple-500/15 text-purple-400";

        const SPAN_COLOR_MAP: Record<string, string> = {
          emotional: "bg-red-500/20 text-red-400",
          authority: "bg-yellow-500/20 text-yellow-400",
          meta:      "bg-purple-500/20 text-purple-400",
        };
        const SPAN_LABEL_MAP: Record<string, string> = {
          emotional: "🔴 emocional",
          authority: "🟡 autoridad",
          meta:      "🟣 meta",
        };

        return (
          <div className="space-y-2">
            {msg.isRejected && (
               <div className="flex items-center gap-2 text-red-400 text-[10px] font-bold tracking-widest uppercase mb-1">
                 <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></span>
                 Acceso Denegado por Protocolo
               </div>
            )}
            {msg.alertLevel === "warning" && (
              <div className="flex items-center gap-2 text-xs text-white mb-1 font-medium bg-amber-500/10 inline-flex px-2 py-1 rounded">
                <span>⚠️</span> Confianza media en la respuesta
              </div>
            )}
            {msg.alertLevel === "critical" && (
              <div className="flex items-center gap-2 text-xs text-white mb-1 font-bold bg-red-500/10 inline-flex px-2 py-1 rounded">
                <span>🚨</span> Baja confiabilidad — revisar contenido
              </div>
            )}
            <p className={`text-sm leading-relaxed pr-12 ${msg.isRejected ? "text-red-400/80 font-medium italic" : "text-white"}`}>
              {msg.content}
            </p>

            {/* ─── RAW INSPECTOR (Modo Auditoría) ──────────────────── */}
            {inspecting && msg.role === "anima" && (msg.raw || msg.rawAttempt) && (
              <div className="mt-3 border border-zinc-700/60 rounded-xl overflow-hidden bg-black/50">

                {/* Header */}
                <div className="flex items-center justify-between px-3 py-2 bg-zinc-900/80 border-b border-zinc-700/40">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                    <span className="text-[9px] font-bold tracking-[0.25em] uppercase text-zinc-400">RAW INSPECTOR</span>
                  </div>
                  {analysis && (
                    <span className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${typeBadgeClass}`}>
                      {types.join(" + ")}
                    </span>
                  )}
                </div>

                <div className="p-3 space-y-3">

                  {/* Barra de confianza */}
                  {analysis && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Confianza del modelo</span>
                        <span className={`text-[10px] font-bold font-mono ${confidenceTextClass}`}>
                          {confidencePct}%
                        </span>
                      </div>
                      <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                        {/* width via CSS var — evita inline style */}
                        <div
                          className={`h-full rounded-full transition-all ${confidenceBarClass} confidence-bar`}
                          data-pct={confidencePct}
                          ref={el => { if (el) el.style.width = `${confidencePct}%`; }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Flags de humo */}
                  {flags.length > 0 && (
                    <div>
                      <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1.5">Señales detectadas</div>
                      <div className="flex flex-wrap gap-1">
                        {flags.map((flag, i) => (
                          <span
                            key={i}
                            className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20"
                          >
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Fragmentos de humo (snippets) */}
                  {smokeSignals.length > 0 && (
                    <div>
                      <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1.5">Fragmentos de humo</div>
                      <div className="space-y-1">
                        {smokeSignals.map((snippet, i) => (
                          <div
                            key={i}
                            className="text-[10px] font-mono text-amber-300/80 bg-amber-500/5 border border-amber-500/15 px-2 py-1 rounded-lg"
                          >
                            &ldquo;{snippet}&rdquo;
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Texto crudo — CON RESALTADO INLINE DE HUMO */}
                  {rawText && rawText !== msg.content && (
                    <div>
                      <div className="text-[9px] text-zinc-500 uppercase tracking-widest mb-1.5">
                        Crudo del modelo
                        {parseMode && (
                          <span className="ml-2 text-zinc-600">[{parseMode}]</span>
                        )}
                        {spans.length > 0 && (
                          <span className="ml-2 text-amber-600/70">
                            ⋄ {spans.length} span{spans.length !== 1 ? "s" : ""} marcado{spans.length !== 1 ? "s" : ""}
                          </span>
                        )}
                      </div>

                      {/* Leyenda de colores — solo tipos presentes */}
                      {spans.length > 0 && (
                        <div className="flex gap-2 mb-2">
                          {(["emotional", "authority", "meta"] as const).map(spanType => {
                            if (!spans.some(s => s.type === spanType)) return null;
                            return (
                              <span
                                key={spanType}
                                className={`text-[8px] font-mono px-1.5 py-0.5 rounded ${SPAN_COLOR_MAP[spanType]}`}
                              >
                                {SPAN_LABEL_MAP[spanType]}
                              </span>
                            );
                          })}
                        </div>
                      )}

                      {/* Texto con spans resaltados */}
                      <pre className="text-[10px] font-mono text-zinc-400 whitespace-pre-wrap leading-relaxed bg-zinc-900/60 p-2 rounded-lg border border-zinc-800">
                        {spans.length > 0
                          ? renderHighlightedText(rawText, spans)
                          : rawText
                        }
                      </pre>
                    </div>
                  )}

                </div>
              </div>
            )}
            
            {/* ─── INSIGHT RENDERING (Detective Contextual) ──────────── */}
            {msg.insight && <InsightMessage insight={msg.insight} />}
          </div>
        );
      }
    }
  };

  // Transformador de URLs para incrustación soberana segura
  const getSafeWebUrl = (url: string | null): { url: string | null; isBlocked: boolean } => {
    if (!url) return { url: null, isBlocked: false };
    
    // Convertir enlace de video de YouTube a versión embed
    const youtubeMatch = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/);
    if (youtubeMatch) {
      return { url: `https://www.youtube.com/embed/${youtubeMatch[1]}`, isBlocked: false };
    }
    
    // Solo bloquear dominios CONFIRMADOS que usan X-Frame-Options: DENY
    // (la mayoría de sitios grandes lo hacen, pero intentamos embed primero para los demás)
    const HARD_BLOCKED = [
      /^(https?:\/\/)?(www\.|m\.)?(youtube\.com)\/?$/i,        // YouTube homepage (videos sí se puede embed)
      /^(https?:\/\/)?(www\.)?(google\.com|google\.com\.ar)\/?$/i, // Google Search
      /^(https?:\/\/)?(www\.)?(facebook|instagram|x|twitter)\.com/i, // Redes sociales
      /^(https?:\/\/)?(www\.)?github\.com/i,                    // GitHub
      /^(https?:\/\/)?(www\.)?chatgpt\.com/i,                   // ChatGPT/OpenAI
    ];
    
    for (const pattern of HARD_BLOCKED) {
      if (pattern.test(url)) {
        return { url, isBlocked: true };
      }
    }

    return { url, isBlocked: false };
  };

  const { url: safeUrl, isBlocked } = getSafeWebUrl(webUrl);

  const handleOverride = async (action: string, content: string, intentionId?: string) => {
    try {
      const res = await fetch("/api/anima/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, content, intention_id: intentionId })
      });
      
      const data = await res.json();
      
      if (data.status === "Authorized") {
        // En un caso real, aquí actualizaríamos el estado local de mensajes 
        // para reemplazar el bloqueado por la respuesta autorizada.
        // Por ahora simulamos el envío de vuelta al chat como un nuevo mensaje del sistema.
        onSendMessage?.(`[MANDATO OPERADOR: ${action.toUpperCase()}] ${data.content.slice(0, 50)}...`);
      } else if (action === "retry_strict" && data.content) {
         onSendMessage?.(data.content);
      }
    } catch (e) {
      console.error("Override failed", e);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#0b141a]">
      {/* Header estilo WhatsApp */}
      <div className="flex items-center px-4 py-3 shadow-md bg-[#1f2c34] z-10">
        {/* Botón Volver para móvil */}
        <button 
          onClick={() => onBack?.()} 
          className="mr-3 md:hidden p-1 rounded-full hover:bg-white/10 text-gray-400"
          aria-label="Volver"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>

        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center mr-3">
          <span className="text-white text-lg font-bold">A</span>
        </div>
        <div className="flex-1">
          <h2 className="text-white font-semibold text-base">Anima</h2>
          <p className="text-emerald-400 text-xs">
            {listening ? '🎙️ Escuchando...' : 'En línea'}
          </p>
        </div>

        <div className="flex items-center gap-1">
          {isSpeaking && (
            <>
              <button
                onClick={toggleVoice}
                title={isVoicePaused ? 'Reanudar Voz' : 'Pausar Voz'}
                aria-label={isVoicePaused ? 'Reanudar Voz' : 'Pausar Voz'}
                className="p-1 px-2 rounded-lg bg-white/5 hover:bg-white/10 text-emerald-400 transition-all flex items-center gap-1.5"
              >
                {isVoicePaused ? <Play size={14} fill="currentColor" /> : <Pause size={14} fill="currentColor" />}
                <span className="text-[10px] font-bold uppercase tracking-tighter">Voz</span>
              </button>
              <button
                onClick={stopVoice}
                title="Detener Voz"
                aria-label="Detener Voz"
                className="p-1.5 rounded-full hover:bg-white/10 text-red-400"
              >
                <Square size={14} fill="currentColor" />
              </button>
            </>
          )}
          
          <button
            onClick={() => setInspecting(!inspecting)}
            title={inspecting ? 'Desactivar Auditoría' : 'Activar Modo Auditoría (Doble Exposición)'}
            className={`p-2 rounded-full transition-all duration-300 ${inspecting
              ? 'bg-magenta-500/20 text-magenta-500 shadow-[0_0_10px_magenta]'
              : 'hover:bg-white/10 text-gray-400'
              }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" strokeWidth="2" />
              <circle cx="12" cy="12" r="3" fill="currentColor" />
              {inspecting && (
                 <path d="M12 2v2M12 20v2M2 12h2M20 12h2" strokeWidth="2" strokeLinecap="round"/>
              )}
            </svg>
          </button>

          <button
            onClick={toggleListening}
            title={listening ? 'Detener escucha' : 'Activar escucha'}
            aria-label={listening ? 'Detener escucha' : 'Activar escucha'}
            className={`p-2 rounded-full transition-all duration-300 ${listening
              ? 'bg-red-500 animate-pulse'
              : 'hover:bg-white/10'
              }`}
          >
            <svg className="w-6 h-6 text-gray-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Área de Contenido Principal (Chat Único) */}
      <div className="flex-1 relative overflow-hidden bg-[#0b141a]">
        
        {/* VISTA: CHAT (Anima) - Siempre Visible */}
        <div className="absolute inset-0 flex flex-col">
          <div className="flex-1 overflow-y-auto px-3 py-4 wa-background">
            <div className="space-y-3">
              {messages.map((msg, i) => {
                const isTool = msg.source === 'tool' || msg.originType === 'tool';
                const isConversation = msg.mode === 'conversation' || !msg.mode;
                const isAnima = msg.role === 'anima';
                const isIntention = msg.mode === 'intention';
                
                if (isAnima && !isTool && !isConversation && !isIntention && msg.type !== 'strategy') return null;

                let displayContent = msg.content;
                if (typeof displayContent === 'string' && displayContent.includes("[resultado actual")) {
                   displayContent = displayContent.split("[resultado actual")[0].trim();
                   if (!displayContent) return null;
                }

                return (
                  <div key={i} className="flex flex-col gap-1 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    
                    {/* Renderizado Estricto basado en Type (ACSP) */}
                    {msg.type === "tool" ? (
                      <ToolMessage content={msg.content} meta={msg} />
                    ) : msg.type === "strategy" ? (
                      <StrategyMessage content={msg.content || msg.options} onExecuteOption={onExecuteOption} intentionId={msg.intentionId} />
                    ) : (
                      <>
                        <LLMMessage content={msg.content} role={msg.role} formatTime={formatTime} spans={msg?.analysis?.smoke_spans} />
                        {msg.insight && <ContextualMemoryTimeline insight={msg.insight} />}
                        <OverridePanel msg={msg} onOverride={handleOverride} />
                      </>
                    )}

                    {/* Inspector de Trazas (Opcional, para debug visible de OS) */}
                    {msg.trace && msg.role === 'anima' && (
                      <div className="mt-0 mb-6 flex justify-start ml-10">
                        <button
                          onClick={() => setOpenTrace(openTrace === i ? null : i)}
                          className={`text-[9px] font-bold uppercase tracking-widest px-2 py-1 rounded transition-all flex items-center gap-2 ${
                            openTrace === i ? 'bg-blue-500/20 text-blue-400' : 'bg-white/5 text-zinc-600 hover:text-zinc-400'
                          }`}
                        >
                          <Cpu size={10} className={openTrace === i ? 'animate-spin-slow' : ''} />
                          {openTrace === i ? "ocultar auditoría" : "ver traza"}
                        </button>
                        {openTrace === i && (
                          <div className="absolute left-0 right-0 mt-8 z-50 bg-black/90 border border-zinc-800 rounded-lg p-4 text-[10px] font-mono space-y-3 max-h-[300px] overflow-y-auto shadow-2xl backdrop-blur-xl">
                            {msg.trace.map((t: any, idx: number) => (
                              <div key={idx} className="border-b border-zinc-800 pb-2 last:border-0">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-blue-400 font-bold uppercase tracking-wider">{t.step}</span>
                                  <span className="text-[8px] text-zinc-600">COMPLETED</span>
                                </div>
                                <div className="bg-zinc-950 p-2 rounded text-zinc-400 overflow-x-auto">
                                  {typeof t.data === 'object' ? JSON.stringify(t.data, null, 2) : String(t.data)}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Sugerencia inteligente */}
              {suggestion && (
                <div className="flex justify-center mt-4 mb-4">
                  <button
                    onClick={() => openWebPage(suggestion.name)}
                    className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center gap-2"
                  >
                    <span className="text-lg">🌐</span>
                    ¿Querés abrir {suggestion.name}?
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* VENTANA FLOTANTE SOBERANA */}
        {webUrl && (
          <div className="absolute inset-0 z-50 flex flex-col md:items-center md:justify-center animate-in fade-in zoom-in-95 duration-200 backdrop-blur-sm bg-black/40 p-2 md:p-8">
            <div className="bg-[#1f2c34] md:w-full md:max-w-4xl h-full md:h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10 md:mt-[-5%] w-full">
              {/* Header de la ventana */}
              <div className="bg-[#111b21] px-4 py-3 flex items-center justify-between border-b border-white/5 cursor-move">
                <div className="flex items-center gap-2">
                   {webUrl.includes('youtube') ? <Youtube size={16} className="text-red-500" /> : <Globe size={16} className="text-blue-400" />}
                   <span className="text-xs font-bold text-white tracking-widest uppercase truncate max-w-[150px] md:max-w-xs">{webTitle}</span>
                </div>
                <div className="flex items-center gap-3">
                   <button 
                     onClick={() => {
                        const url = webUrl;
                        setWebUrl(null);
                        setTimeout(() => setWebUrl(url), 10);
                     }} 
                     className="text-zinc-400 hover:text-white"
                     aria-label="Recargar"
                     title="Recargar"
                   >
                     <RotateCw size={14} />
                   </button>
                   <button 
                     onClick={() => window.open(webUrl, '_blank')}
                     className="text-zinc-400 hover:text-white"
                     title="Abrir externa"
                   >
                     <ExternalLink size={14} />
                   </button>
                   <button 
                     onClick={() => setWebUrl(null)}
                     className="bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition-colors p-1 rounded-full ml-1"
                     title="Cerrar"
                     aria-label="Cerrar Nodo"
                   >
                     <X size={16} />
                   </button>
                </div>
              </div>
              
              {/* Iframe del Nodo o Fallback Soberano */}
              <div className="flex-1 bg-[#0b141a] relative flex items-center justify-center">
                {isBlocked ? (
                  <div className="text-center p-8 flex flex-col items-center animate-in fade-in duration-500">
                     <Shield size={48} className="text-blue-500/50 mb-4" />
                     <h3 className="text-white font-bold text-lg mb-2 uppercase tracking-wide">Restricción de Soberanía Detectada</h3>
                     <p className="text-zinc-400 text-sm max-w-sm mb-6 leading-relaxed">
                       El sitio <strong className="text-blue-400">{webUrl}</strong> bloquea su ejecución dentro de nodos embebidos por políticas de seguridad externas (X-Frame-Options).
                     </p>
                     <button
                       onClick={() => window.open(webUrl, '_blank')}
                       className="bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600 hover:text-white font-bold py-2.5 px-6 rounded-full flex items-center gap-2 transition-all"
                     >
                       <ExternalLink size={16} />
                       Abrir en Dominio Externo
                     </button>
                  </div>
                ) : (
                  <iframe 
                    src={safeUrl || ''} 
                    className="absolute inset-0 w-full h-full border-none bg-white" 
                    title={webTitle}
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    onError={() => {
                      // Si el iframe falla por CORS/X-Frame, abrir externamente
                      console.warn('⚠️ [WebView] iframe bloqueado, abriendo externa');
                      window.open(webUrl!, '_blank');
                      setWebUrl(null);
                    }}
                  />
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Área de input estilo WhatsApp */}
      <div className="px-2 py-2 flex items-center gap-2 bg-[#1f2c34] border-t border-white/5 pb-safe">
        {/* Botón emoji */}
        <button className="p-2 rounded-full hover:bg-white/10 transition-colors" aria-label="Emojis">
          <svg className="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
          </svg>
        </button>

        {/* Input de texto */}
        <div className="flex-1 relative">
          <input
            type="text"
            className="w-full px-4 py-2.5 rounded-full text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 bg-[#2a3942]"
            placeholder="Escribe un mensaje..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
          />
        </div>

        {/* Botón de enviar o micrófono */}
        {input.trim() ? (
          <button
            onClick={handleSend}
            className="p-3 rounded-full bg-emerald-500 hover:bg-emerald-600 transition-colors shadow-lg"
            aria-label="Enviar mensaje"
          >
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        ) : (
          <button
            onClick={toggleListening}
            aria-label={listening ? 'Detener grabación' : 'Activar micrófono'}
            className={`p-3 rounded-full transition-all duration-300 shadow-lg ${listening
              ? 'bg-red-500 animate-pulse'
              : 'bg-emerald-500 hover:bg-emerald-600'
              }`}
          >
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z" />
            </svg>
          </button>
        )}
      </div>
      
      {/* Panel de Auditoría en Tiempo Real (BUG-05) */}
      <RealTimeAuditLog />
    </div>
  );
}
