import React, { useState, useRef, useEffect } from 'react';
import { Zap, Code, FolderTree, CheckCircle, AlertCircle, Loader, Eye, Play, X } from 'lucide-react';

import { API_BASE } from '../core/config';

// Estados del flujo cognitivo
const STATES = {
  IDLE: 'idle',
  INTERPRETING: 'interpreting',
  REVIEW_INTERPRETATION: 'review_interpretation',
  PLANNING: 'planning',
  REVIEW_PLAN: 'review_plan',
  GENERATING: 'generating',
  COMPLETE: 'complete',
  ERROR: 'error'
};

interface Interpretation {
  description: string;
  project_type: string;
  project_name: string;
  features?: string[];
  technologies?: Record<string, string[]>;
}

interface Plan {
  structure?: Record<string, string[]>;
  dependencies?: Record<string, string[]>;
  files?: Record<string, string>;
}

interface Result {
  files_created: number;
  project_path: string;
  files?: { filename: string; category: string; size: number }[];
  errors?: { filename: string; error: string }[];
  status?: string;
  error?: string;
}

interface ProgressItem {
  message: string;
  type: string;
  timestamp: number;
}

export default function DeveloperInterface() {
  const [state, setState] = useState(STATES.IDLE);
  const [input, setInput] = useState('');
  const [interpretation, setInterpretation] = useState<Interpretation | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ProgressItem[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [progress]);

  const addProgress = (message: string, type: string = 'info') => {
    setProgress(prev => [...prev, { message, type, timestamp: Date.now() }]);
  };

  const reset = () => {
    setState(STATES.IDLE);
    setInput('');
    setInterpretation(null);
    setPlan(null);
    setResult(null);
    setError(null);
    setProgress([]);
  };

  // Fase 1: Interpretar lenguaje natural
  const interpretInput = async () => {
    setState(STATES.INTERPRETING);
    addProgress('Anima Developer está interpretando tu intención...', 'system');
    
    try {
      const res = await fetch(`${API_BASE}/developer/interpret`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: input })
      });
      
      const data = await res.json();
      
      if (data.status === 'success') {
        setInterpretation(data.interpretation);
        setState(STATES.REVIEW_INTERPRETATION);
        addProgress('Interpretación completada. Revisá antes de continuar.', 'success');
      } else {
        throw new Error(data.error || 'Error en interpretación');
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      setState(STATES.ERROR);
      addProgress(`Error: ${errorMsg}`, 'error');
    }

  };

  // Fase 2: Planificar proyecto
  const planProject = async () => {
    setState(STATES.PLANNING);
    addProgress('Anima Developer está planificando la arquitectura...', 'system');
    
    try {
      const res = await fetch(`${API_BASE}/developer/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: interpretation?.description,
          project_type: interpretation?.project_type
        })
      });
      
      const data = await res.json();
      
      if (data.status === 'success') {
        setPlan(data.plan);
        setState(STATES.REVIEW_PLAN);
        addProgress('Plan arquitectónico listo. Revisá la estructura antes de materializar.', 'success');
      } else {
        throw new Error(data.error || 'Error en planificación');
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      setState(STATES.ERROR);
      addProgress(`Error: ${errorMsg}`, 'error');
    }
  };

  // Fase 3: Generar proyecto completo
  const generateProject = async () => {
    setState(STATES.GENERATING);
    addProgress('Iniciando materialización del proyecto...', 'system');
    
    try {
      const res = await fetch(`${API_BASE}/developer/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: interpretation?.description,
          project_type: interpretation?.project_type
        })
      });
      
      const data = await res.json();
      
      if (data.status === 'success' || data.status === 'partial') {
        setResult(data);
        setState(STATES.COMPLETE);
        addProgress(`Proyecto materializado: ${data.files_created} archivos creados`, 'success');
        
        if (data.errors && data.errors.length > 0) {
          addProgress(`Advertencias: ${data.errors.length} archivos con problemas`, 'warning');
        }
      } else {
        throw new Error(data.error || 'Error en generación');
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      setState(STATES.ERROR);
      addProgress(`Error: ${errorMsg}`, 'error');
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      {/* Panel Principal */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Zap className="text-purple-400" size={28} />
              <div>
                <h1 className="text-xl font-bold">Anima Developer</h1>
                <p className="text-xs text-slate-500">Sistema de Materialización Cognitiva</p>
              </div>
            </div>
            
            {state !== STATES.IDLE && (
              <button
                onClick={reset}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors text-sm"
              >
                <X size={16} />
                Resetear
              </button>
            )}
          </div>
        </header>

        {/* Área de Trabajo */}
        <div className="flex-1 overflow-hidden flex">
          {/* Input Principal */}
          {state === STATES.IDLE && (
            <div className="flex-1 flex flex-col items-center justify-center p-8">
              <div className="max-w-2xl w-full space-y-6">
                <div className="text-center space-y-2">
                  <h2 className="text-3xl font-serif text-slate-100">¿Qué querés construir?</h2>
                  <p className="text-slate-400">Describí tu idea en lenguaje natural. Anima Developer se encargará del resto.</p>
                </div>
                
                <div className="space-y-4">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ejemplo: 'Quiero una app para gestionar tareas con calendario y recordatorios'"
                    className="w-full h-48 bg-slate-900 border border-slate-700 rounded-2xl p-6 text-lg resize-none focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
                  />
                  
                  <button
                    onClick={interpretInput}
                    disabled={!input.trim()}
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed py-4 rounded-2xl font-bold text-lg shadow-lg shadow-purple-900/20 transition-all active:scale-[0.98]"
                  >
                    Iniciar Proceso Cognitivo
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Review de Interpretación */}
          {state === STATES.REVIEW_INTERPRETATION && interpretation && (
            <div className="flex-1 overflow-auto p-8">
              <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center gap-3 text-purple-400">
                  <Eye size={24} />
                  <h2 className="text-2xl font-bold">Interpretación de Intención</h2>
                </div>
                
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Nombre del Proyecto</div>
                    <div className="text-xl font-semibold text-slate-100">{interpretation.project_name}</div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Tipo</div>
                    <div className="inline-flex px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">
                      {interpretation.project_type}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Descripción Técnica</div>
                    <div className="text-slate-300 leading-relaxed">{interpretation.description}</div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Features Principales</div>
                    <div className="flex flex-wrap gap-2">
                      {interpretation.features?.map((feature, i) => (
                        <span key={i} className="px-3 py-1 bg-slate-800 text-slate-300 rounded-lg text-sm">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Stack Técnico</div>
                    <div className="space-y-2">
                      {Object.entries(interpretation.technologies || {}).map(([category, techs]) => (
                        <div key={category} className="flex gap-2 items-start">
                          <span className="text-xs text-slate-500 uppercase min-w-[80px]">{category}:</span>
                          <div className="flex flex-wrap gap-1">
                            {techs.map((tech, i) => (
                              <span key={i} className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs">
                                {tech}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-slate-800 flex gap-3">
                    <button
                      onClick={() => setState(STATES.IDLE)}
                      className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
                    >
                      Ajustar Idea
                    </button>
                    <button
                      onClick={planProject}
                      className="flex-1 py-3 bg-purple-600 hover:bg-purple-500 rounded-xl font-semibold transition-colors"
                    >
                      Continuar a Planificación
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Review de Plan */}
          {state === STATES.REVIEW_PLAN && plan && (
            <div className="flex-1 overflow-auto p-8">
              <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center gap-3 text-blue-400">
                  <FolderTree size={24} />
                  <h2 className="text-2xl font-bold">Plan Arquitectónico</h2>
                </div>
                
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-3">Estructura del Proyecto</div>
                    {Object.entries(plan.structure || {}).map(([category, files]) => (
                      <div key={category} className="mb-4">
                        <div className="text-sm font-semibold text-slate-400 mb-2">📁 {category}/</div>
                        <div className="ml-4 space-y-1">
                          {files.map((file, i) => (
                            <div key={i} className="flex items-center gap-2 text-sm text-slate-300">
                              <Code size={14} className="text-slate-500" />
                              <span>{file}</span>
                              {plan.files?.[file] && (
                                <span className="text-xs text-slate-500 italic ml-2">
                                  — {plan.files[file].substring(0, 60)}...
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Dependencias</div>
                    <div className="space-y-2">
                      {Object.entries(plan.dependencies || {}).map(([lang, deps]) => (
                        deps.length > 0 && (
                          <div key={lang} className="flex gap-2 items-start">
                            <span className="text-xs text-slate-500 uppercase min-w-[80px]">{lang}:</span>
                            <div className="flex flex-wrap gap-1">
                              {deps.map((dep, i) => (
                                <span key={i} className="px-2 py-0.5 bg-green-500/20 text-green-300 rounded text-xs">
                                  {dep}
                                </span>
                              ))}
                            </div>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-slate-800 flex gap-3">
                    <button
                      onClick={() => setState(STATES.REVIEW_INTERPRETATION)}
                      className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
                    >
                      Volver a Interpretación
                    </button>
                    <button
                      onClick={generateProject}
                      className="flex-1 py-3 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-500 hover:to-blue-500 rounded-xl font-semibold transition-colors shadow-lg"
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Play size={18} />
                        Materializar Proyecto
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Estados de Procesamiento */}
          {(state === STATES.INTERPRETING || state === STATES.PLANNING || state === STATES.GENERATING) && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <Loader className="animate-spin text-purple-400 mx-auto" size={48} />
                <div className="text-xl font-semibold">
                  {state === STATES.INTERPRETING && 'Interpretando intención...'}
                  {state === STATES.PLANNING && 'Planificando arquitectura...'}
                  {state === STATES.GENERATING && 'Materializando proyecto...'}
                </div>
                <div className="text-sm text-slate-500">Anima Developer está trabajando</div>
              </div>
            </div>
          )}

          {/* Resultado Final */}
          {state === STATES.COMPLETE && result && (
            <div className="flex-1 overflow-auto p-8">
              <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center gap-3 text-green-400">
                  <CheckCircle size={24} />
                  <h2 className="text-2xl font-bold">Proyecto Materializado</h2>
                </div>
                
                <div className="bg-slate-900 border border-green-800/30 rounded-2xl p-6 space-y-4">
                  <div className="text-center py-4">
                    <div className="text-6xl font-bold text-green-400">{result.files_created}</div>
                    <div className="text-slate-400 mt-2">archivos creados exitosamente</div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Ubicación</div>
                    <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-sm text-slate-300">
                      {result.project_path}
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Archivos</div>
                    <div className="space-y-1 max-h-64 overflow-auto">
                      {result.files?.map((file, i) => (
                        <div key={i} className="flex items-center justify-between bg-slate-950 border border-slate-800 rounded-lg p-3">
                          <div className="flex items-center gap-2">
                            <Code size={14} className="text-blue-400" />
                            <span className="text-sm text-slate-300">{file.filename}</span>
                            <span className="text-xs text-slate-600">({file.category})</span>
                          </div>
                          <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {result.errors && result.errors.length > 0 && (
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                      <div className="text-sm font-semibold text-yellow-400 mb-2">Advertencias</div>
                      {result.errors.map((err, i) => (
                        <div key={i} className="text-xs text-yellow-300">
                          {err.filename}: {err.error}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <button
                    onClick={reset}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-500 rounded-xl font-semibold transition-colors"
                  >
                    Crear Otro Proyecto
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {state === STATES.ERROR && (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="max-w-md w-full text-center space-y-4">
                <AlertCircle className="text-red-400 mx-auto" size={48} />
                <h2 className="text-xl font-bold text-red-400">Error en el Proceso</h2>
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-sm text-red-300">{error}</p>
                </div>
                <button
                  onClick={reset}
                  className="w-full py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
                >
                  Reintentar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Panel de Progreso Cognitivo */}
      <aside className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h3 className="font-semibold text-slate-300">Proceso Cognitivo</h3>
          <p className="text-xs text-slate-500 mt-1">Trazabilidad completa del flujo</p>
        </div>
        
        <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-2">
          {progress.length === 0 && (
            <div className="text-center text-slate-600 text-sm py-8">
              Sin actividad aún
            </div>
          )}
          
          {progress.map((item, i) => (
            <div 
              key={item.timestamp} 
              className={`p-3 rounded-lg text-sm border ${
                item.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-300' :
                item.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-300' :
                item.type === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300' :
                'bg-slate-800 border-slate-700 text-slate-400'
              }`}
            >
              <div className="flex items-start gap-2">
                <span className="text-xs text-slate-600">{new Date(item.timestamp).toLocaleTimeString()}</span>
                <span className="flex-1">{item.message}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}