import React, { useState, useEffect, useRef } from 'react';
import { 
  Zap, Code, FolderTree, CheckCircle, AlertCircle, Loader, 
  Terminal, Package, ArrowRight, Play, RefreshCw, Layers,
  Layout, Cpu, Database, Globe, Github
} from 'lucide-react';
import { API_BASE } from '../core/config';

// Protocolo de Estados IDE
const IDE_STATES = {
  IDLE: 'idle',
  DISCUSSING: 'discussing',
  MANIFEST_READY: 'manifest_ready',
  BLUEPRINT_VIEW: 'blueprinting',
  MATERIALIZING: 'materializing',
  OPERATIONALIZING: 'operationalizing',
  SUCCESS: 'success',
  ERROR: 'error'
};

interface FileItem {
  path: string;
  description: string;
  priority: string;
  status: 'pending' | 'generating' | 'completed' | 'error';
}

interface Manifest {
  type: string;
  structure: string[];
  connection: string;
  impact: string;
}

interface ProjectPlan {
  project_id: string;
  project_name: string;
  archetype: string;
  files: FileItem[];
  dependencies: string[];
  rationale: string;
  manifest?: Manifest;
}

export default function HighEndDeveloperUI() {
  const [state, setState] = useState(IDE_STATES.IDLE);
  const [prompt, setPrompt] = useState('');
  const [plan, setPlan] = useState<ProjectPlan | null>(null);
  const [currentFileIndex, setCurrentFileIndex] = useState(-1);
  const [logs, setLogs] = useState<{msg: string, type: 'info' | 'success' | 'warning' | 'error'}[]>([]);
  const [error, setError] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll para logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (msg: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    setLogs(prev => [...prev, { msg, type }]);
  };

  const handleOperatorRequest = async () => {
    if (!prompt.trim()) return;
    
    setError(null);
    setLogs([]);
    setState(IDE_STATES.DISCUSSING);
    addLog(`🔍 Interpretando solicitud: "${prompt}"`, 'info');

    try {
      // 1. Interpretación (Obtener Manifest)
      const interpretRes = await fetch(`${API_BASE}/developer/interpret`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: prompt })
      });
      const interpretData = await interpretRes.json();

      if (interpretData.status !== 'success' && !interpretData.technical_description) {
         throw new Error('No se pudo interpretar la solicitud técnica.');
      }

      // Mapear respuesta al nuevo protocolo de 5 puntos
      const manifest: Manifest = {
        type: interpretData.project_type || 'Módulo Interno',
        structure: interpretData.features || ['Análisis de arquitectura en curso...'],
        connection: `Vínculo detectado con: ${interpretData.tags?.join(', ') || 'Core System'}`,
        impact: `Requiere inyección de ${interpretData.technologies?.length || 0} librerías y cambios en el mapa de Nexus.`
      };

      setPlan({
        project_id: 'PENDING',
        project_name: interpretData.project_name || 'Nuevo Componente',
        archetype: interpretData.project_type || 'Custom',
        files: [],
        dependencies: interpretData.technologies || [],
        rationale: interpretData.technical_description,
        manifest: manifest
      });

      setState(IDE_STATES.MANIFEST_READY);
      addLog('📋 Manifiesto térmico generado. Esperando autorización del Operador.', 'warning');
    } catch (err: any) {
      setError(err.message);
      setState(IDE_STATES.ERROR);
      addLog(`❌ ERROR DE INTERPRETACIÓN: ${err.message}`, 'error');
    }
  };

  const startMaterialization = async (isSandbox = false) => {
    if (!plan) return;
    
    setState(IDE_STATES.BLUEPRINT_VIEW);
    addLog(isSandbox ? '🧪 Iniciando Simulación en modo SANDBOX...' : '🚀 Iniciando MATERIALIZACIÓN REAL en el sistema...', 'info');

    try {
      // 1. Blueprinting (Planificación real)
      const planRes = await fetch(`${API_BASE}/developer/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: isSandbox ? `[SANDBOX_MODE] ${prompt}` : prompt })
      });
      const planData = await planRes.json();

      if (planData.status !== 'success') throw new Error(planData.message || 'Planificación fallida');
      
      const projectPlan: ProjectPlan = {
        ...planData.plan,
        files: planData.plan.files.map((f: any) => ({ ...f, status: 'pending' })),
        manifest: plan?.manifest
      };
      
      setPlan(projectPlan);
      addLog(`✅ Arquitectura definida: ${projectPlan.archetype}`, 'success');

      // 2. Materialización (Generación de archivos)
      setState(IDE_STATES.MATERIALIZING);
      addLog('🛠️ Fase: Materialización Granular', 'info');
      
      for (let i = 0; i < projectPlan.files.length; i++) {
        setCurrentFileIndex(i);
        const file = projectPlan.files[i];
        addLog(`📄 Generando [${i+1}/${projectPlan.files.length}]: ${file.path}...`, 'info');
        
        const genRes = await fetch(`${API_BASE}/developer/generate-file`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            project_id: projectPlan.project_id,
            file_path: file.path,
            context: projectPlan.rationale
          })
        });
        
        if (!genRes.ok) throw new Error(`Error generando ${file.path}`);
        addLog(`✨ ${file.path} completado.`, 'success');
        
        setPlan(prev => {
          if (!prev) return null;
          const newFiles = [...prev.files];
          newFiles[i].status = 'completed';
          return { ...prev, files: newFiles };
        });
      }

      if (isSandbox) {
        setState(IDE_STATES.SUCCESS);
        addLog('🏁 SIMULACIÓN FINALIZADA. Revisa el directorio temporal.', 'success');
        return;
      }

      // 3. Operacionalización (Instalación)
      setState(IDE_STATES.OPERATIONALIZING);
      addLog('📦 Operacionalizando en el ecosistema...', 'info');
      
      const installRes = await fetch(`${API_BASE}/developer/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectPlan.project_id })
      });
      
      if (!installRes.ok) addLog('⚠️ Instalador finalizado con avisos.', 'warning');
      else addLog('🚀 Módulo integrado y operacional.', 'success');

      setState(IDE_STATES.SUCCESS);
      addLog('🏆 MATERIALIZACIÓN CULMINADA.', 'success');

    } catch (err: any) {
      console.error(err);
      setError(err.message);
      setState(IDE_STATES.ERROR);
      addLog(`❌ ERROR CRÍTICO: ${err.message}`, 'error');
    }
  };

  return (
    <div className="flex h-full w-full bg-[#0a0a0b] text-slate-300 font-sans overflow-hidden">
      
      {/* COLUMNA 1: OPERATOR CONSOLE (Chat & Logs) */}
      <div className="w-[30%] border-r border-white/5 flex flex-col bg-[#0f1115]">
        <div className="p-6 border-bottom border-white/5 bg-[#14171d]">
          <h2 className="text-xl font-bold text-white flex items-center gap-2 font-premium">
            <Cpu className="text-cyan-400 w-5 h-5" />
            Operator Console
          </h2>
          <p className="text-[10px] text-gray-500 font-mono mt-1">ALEGRIA_IDE_V2.0_SOVEREIGN</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          {logs.map((log, i) => (
            <div key={i} className={`text-xs p-3 rounded-lg border leading-relaxed animate-fade-in ${
              log.type === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-400' :
              log.type === 'error' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
              log.type === 'warning' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400' :
              'bg-blue-500/5 border-white/5 text-blue-300'
            }`}>
              <div className="flex gap-2">
                <span className="opacity-30">[{new Date().toLocaleTimeString()}]</span>
                <span>{log.msg}</span>
              </div>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>

        <div className="p-6 bg-[#14171d] border-t border-white/5">
          {state === IDE_STATES.MANIFEST_READY && plan?.manifest ? (
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
                 <h3 className="text-[11px] font-black text-emerald-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <CheckCircle size={14} /> Manifiesto de Materialización
                 </h3>
                 <div className="space-y-3 font-mono text-[10px] text-slate-400">
                    <div>
                      <span className="text-emerald-500/60">[TIPO]:</span> {plan.manifest.type}
                    </div>
                    <div>
                      <span className="text-emerald-500/60">[ESTRUCTURA]:</span>
                      <ul className="pl-4 mt-1 list-disc opacity-80">
                         {plan.manifest.structure.slice(0, 3).map((f, i) => <li key={i}>{f}</li>)}
                         {plan.manifest.structure.length > 3 && <li>...y {plan.manifest.structure.length - 3} más</li>}
                      </ul>
                    </div>
                    <div>
                      <span className="text-emerald-500/60">[CONEXIÓN]:</span> {plan.manifest.connection}
                    </div>
                    <div>
                      <span className="text-emerald-500/60">[IMPACTO]:</span> {plan.manifest.impact}
                    </div>
                 </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                 <button 
                  onClick={() => setState(IDE_STATES.IDLE)}
                  className="py-3 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-red-500/10 hover:border-red-500/30 transition-all"
                 >
                   Cancelar
                 </button>
                 <button 
                  onClick={() => startMaterialization(false)} // Aquí podría ser un simple Blueprint visual
                  className="py-3 bg-blue-600/20 border border-blue-500/40 text-blue-400 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600/30 transition-all"
                 >
                   Blueprint
                 </button>
                 <button 
                  onClick={() => startMaterialization(true)}
                  className="py-3 bg-purple-600/20 border border-purple-500/40 text-purple-400 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-purple-600/30 transition-all"
                 >
                   Sandbox
                 </button>
                 <button 
                  onClick={() => startMaterialization(false)}
                  className="py-3 bg-emerald-600 text-black rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-500/20"
                 >
                   Instalar
                 </button>
              </div>
            </div>
          ) : (
            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={state !== IDE_STATES.IDLE && state !== IDE_STATES.SUCCESS && state !== IDE_STATES.ERROR}
                placeholder="Describe qué componente o módulo deseas materializar..."
                className="w-full bg-black/40 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:border-cyan-400/50 min-h-[100px] resize-none transition-all custom-scrollbar"
              />
              <button 
                onClick={handleOperatorRequest}
                disabled={state !== IDE_STATES.IDLE && state !== IDE_STATES.SUCCESS && state !== IDE_STATES.ERROR}
                className="absolute bottom-4 right-4 p-3 bg-cyan-500 text-black rounded-xl hover:bg-cyan-400 disabled:opacity-30 disabled:grayscale transition-all shadow-glow-sm"
              >
                {state === IDE_STATES.IDLE ? <Play fill="currentColor" size={18} /> : <RefreshCw className="animate-spin" size={18} />}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* COLUMNA 2: AURA EXPLORER (File System) */}
      <div className="flex-1 flex flex-col bg-black/20">
        <div className="p-6 border-bottom border-white/5 flex justify-between items-center bg-[#0f1115]/50">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2 font-premium">
              <FolderTree className="text-purple-400 w-5 h-5" />
              Aura Explorer
            </h2>
            <p className="text-[10px] text-gray-500 font-mono mt-1">PROJECT_ID: {plan?.project_id || 'NULL'}</p>
          </div>
          {plan && (
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-full text-[10px] font-bold uppercase">
                {plan.archetype}
              </span>
            </div>
          )}
        </div>

        <div className="flex-1 p-8 grid grid-cols-2 gap-6 overflow-y-auto custom-scrollbar">
          {(state === IDE_STATES.MANIFEST_READY) ? (
            <div className="col-span-2 flex flex-col items-center justify-center opacity-40 mt-20 animate-pulse">
               <Cpu size={64} className="mb-4 text-emerald-500" />
               <p className="font-premium text-lg uppercase tracking-widest text-emerald-400">Manifiesto en Espera</p>
               <p className="text-xs text-slate-500 mt-2">Autoriza para iniciar el despliegue de archivos.</p>
            </div>
          ) : plan && plan.files.length > 0 ? (
            plan.files.map((file, i) => (
              <div 
                key={i} 
                className={`p-4 rounded-2xl border transition-all duration-300 ${
                  i === currentFileIndex ? 'bg-cyan-500/5 border-cyan-500/40 shadow-glow-sm' : 
                  file.status === 'completed' ? 'bg-white/5 border-white/10' : 'bg-white/[0.02] border-white/5 opacity-50'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Code size={16} className={i === currentFileIndex ? 'text-cyan-400 animate-pulse' : 'text-gray-500'} />
                    <span className="text-sm font-bold text-white font-mono truncate max-w-[150px]">{file.path}</span>
                  </div>
                  {file.status === 'completed' ? (
                    <CheckCircle size={14} className="text-green-500" />
                  ) : i === currentFileIndex ? (
                    <Loader size={14} className="text-cyan-400 animate-spin" />
                  ) : null}
                </div>
                <p className="text-[10px] text-gray-500 leading-relaxed mb-4">{file.description}</p>
                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-700 ${file.status === 'completed' ? 'w-full bg-green-500/50' : i === currentFileIndex ? 'w-1/2 bg-cyan-500 animate-pulse' : 'w-0'}`}
                  ></div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-2 flex flex-col items-center justify-center opacity-20 mt-20">
              <Layers size={64} className="mb-4" />
              <p className="font-premium text-lg">Esperando Directriz del Operador</p>
            </div>
          )}
        </div>
      </div>

      {/* COLUMNA 3: NEXUS MANAGER (Dependencies & Health) */}
      <div className="w-[30%] border-l border-white/5 flex flex-col bg-[#0f1115]">
        <div className="p-6 border-bottom border-white/5 bg-[#14171d]">
          <h2 className="text-xl font-bold text-white flex items-center gap-2 font-premium">
            <Package className="text-amber-400 w-5 h-5" />
            Nexus Manager
          </h2>
          <p className="text-[10px] text-gray-500 font-mono mt-1">DEPENDENCY_PIPELINE_ACTIVE</p>
        </div>

        <div className="flex-1 p-6 space-y-6 overflow-y-auto custom-scrollbar">
          <section>
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Terminal size={12} />
              Lista de Dependencias
            </h3>
            <div className="space-y-2">
              {plan?.dependencies.map((dep, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-white/[0.03] border border-white/5 rounded-xl hover:bg-white/[0.05] transition-colors">
                  <span className="text-xs font-mono text-amber-200">{dep}</span>
                  <div className="flex gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500/40 shadow-glow-sm"></span>
                  </div>
                </div>
              ))}
              {!plan && <p className="text-xs text-gray-600 italic">No hay proyecto cargado...</p>}
            </div>
          </section>

          <section className="bg-amber-500/5 border border-amber-500/10 rounded-2xl p-6">
            <h3 className="text-sm font-bold text-amber-400 mb-2 flex items-center gap-2">
              <AlertCircle size={16} />
              Health Insight
            </h3>
            <p className="text-[11px] leading-relaxed text-amber-200/60">
              {state === IDE_STATES.OPERATIONALIZING ? 'Detectando package.json... Ejecutando NODE_INSTALL_AUTO.' : 
               state === IDE_STATES.SUCCESS ? 'Sistema en buen estado. Todas las dependencias sincronizadas.' :
               'Esperando despliegue de arquitectura para auditar salud.'}
            </p>
          </section>
        </div>

        <div className="p-6 bg-[#14171d] border-t border-white/5">
           <div className="flex gap-3">
              <button disabled className="flex-1 p-4 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                <Github size={14} /> Git Sync
              </button>
              <button disabled className="flex-1 p-4 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-bold uppercase tracking-widest hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                <Globe size={14} /> Preview
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
