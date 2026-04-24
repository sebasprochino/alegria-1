import React, { useState, useEffect } from 'react';
import { 
  Terminal, 
  Cpu, 
  Code, 
  Play, 
  Save, 
  FileText, 
  Activity,
  Layers,
  GitBranch,
  CheckCircle2,
  Clock,
  AlertCircle
} from 'lucide-react';

const DeveloperView = () => {
  const [activeTab, setActiveTab] = useState('editor');
  const [isProcessing, setIsProcessing] = useState(false);
  const [code, setCode] = useState('// Escribe tu lógica aquí...');
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState({
    cpu: 12,
    memory: 45,
    latency: 120,
    requests: 1450
  });

  // Estado del Planificador
  const [planSteps, setPlanSteps] = useState([
    { id: 1, title: 'Análisis de Requisitos', status: 'completed', duration: '2ms' },
    { id: 2, title: 'Validación Arquitectónica', status: 'processing', duration: '...' },
    { id: 3, title: 'Generación de Código', status: 'pending', duration: '-' },
    { id: 4, title: 'Tests Unitarios', status: 'pending', duration: '-' }
  ]);

  // Simulación de métricas en tiempo real
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        cpu: Math.floor(Math.random() * 30) + 10,
        memory: Math.floor(Math.random() * 20) + 40,
        latency: Math.floor(Math.random() * 50) + 100,
        requests: prev.requests + Math.floor(Math.random() * 5)
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleRun = () => {
    setIsProcessing(true);
    addLog('info', 'Iniciando proceso de compilación...');
    
    // Simular proceso
    setTimeout(() => {
      addLog('success', 'Compilación exitosa (14ms)');
      setIsProcessing(false);
    }, 1500);
  };

  const addLog = (type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { type, message, timestamp }]);
  };

  return (
    <div className="flex h-full bg-[#0b141a] text-[#e9edef]">
      {/* Sidebar de Herramientas */}
      <div className="w-16 border-r border-[#202c33] flex flex-col items-center py-4 gap-4">
        <ToolButton 
          icon={<Code size={20} />} 
          active={activeTab === 'editor'} 
          onClick={() => setActiveTab('editor')}
          tooltip="Editor de Código"
        />
        <ToolButton 
          icon={<Activity size={20} />} 
          active={activeTab === 'monitoring'} 
          onClick={() => setActiveTab('monitoring')}
          tooltip="Métricas del Sistema"
        />
        <ToolButton 
          icon={<GitBranch size={20} />} 
          active={activeTab === 'planner'} 
          onClick={() => setActiveTab('planner')}
          tooltip="Planificador de Tareas"
        />
        <div className="flex-1" />
        <ToolButton 
          icon={<Save size={20} />} 
          onClick={() => addLog('info', 'Proyecto guardado')}
          tooltip="Guardar"
        />
      </div>

      {/* Área Principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 border-b border-[#202c33] flex items-center justify-between px-6 bg-[#111b21]">
          <div className="flex items-center gap-3">
            <Terminal className="text-[#00a884]" size={20} />
            <span className="font-medium">Anima Developer Console</span>
            <span className="text-xs bg-[#202c33] px-2 py-0.5 rounded text-[#8696a0]">v2.4.0</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs text-[#8696a0]">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span>Sistema Online</span>
            </div>
            <button 
              onClick={handleRun}
              disabled={isProcessing}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-colors
                ${isProcessing 
                  ? 'bg-[#202c33] text-[#8696a0] cursor-not-allowed' 
                  : 'bg-[#00a884] hover:bg-[#008f6f] text-white'}`}
            >
              {isProcessing ? <LoaderIcon /> : <Play size={16} />}
              {isProcessing ? 'Ejecutando...' : 'Ejecutar'}
            </button>
          </div>
        </header>

        {/* Contenido Dinámico */}
        <div className="flex-1 overflow-hidden flex">
          {activeTab === 'editor' && (
            <div className="flex-1 flex flex-col">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="flex-1 bg-[#0b141a] p-6 font-mono text-sm resize-none focus:outline-none text-[#e9edef] leading-relaxed"
                spellCheck="false"
              />
              <ConsolePanel logs={logs} />
            </div>
          )}

          {activeTab === 'planner' && (
            <div className="flex-1 p-8 overflow-y-auto">
              <h2 className="text-xl font-light mb-6 flex items-center gap-2">
                <GitBranch className="text-[#00a884]" />
                Cadena de Pensamiento
              </h2>
              <div className="max-w-3xl space-y-4">
                {planSteps.map(step => (
                  <PlanStep key={step.id} step={step} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'monitoring' && (
            <div className="flex-1 p-8 grid grid-cols-2 gap-6">
              <MetricCard 
                title="Uso de CPU" 
                value={`${metrics.cpu}%`} 
                icon={<Cpu size={24} />}
                color="text-blue-400"
              />
              <MetricCard 
                title="Memoria" 
                value={`${metrics.memory} MB`} 
                icon={<Layers size={24} />}
                color="text-purple-400"
              />
              <MetricCard 
                title="Latencia" 
                value={`${metrics.latency} ms`} 
                icon={<Activity size={24} />}
                color="text-green-400"
              />
              <MetricCard 
                title="Peticiones" 
                value={metrics.requests} 
                icon={<FileText size={24} />}
                color="text-yellow-400"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Componentes Auxiliares
const ToolButton = ({ icon, active, onClick, tooltip }) => (
  <button
    onClick={onClick}
    title={tooltip}
    className={`p-3 rounded-xl transition-all duration-200 group relative
      ${active ? 'bg-[#00a884] text-white' : 'text-[#8696a0] hover:bg-[#202c33] hover:text-[#e9edef]'}`}
  >
    {icon}
  </button>
);

const PlanStep = ({ step }) => {
  const getIcon = () => {
    switch(step.status) {
      case 'completed': return <CheckCircle2 size={20} className="text-green-500" />;
      case 'processing': return <LoaderIcon className="text-blue-400" />;
      case 'error': return <AlertCircle size={20} className="text-red-500" />;
      default: return <Clock size={20} className="text-[#8696a0]" />;
    }
  };

  return (
    <div className={`p-4 rounded-lg border border-[#202c33] bg-[#111b21] flex items-center justify-between
      ${step.status === 'processing' ? 'ring-1 ring-[#00a884] bg-[#00a884]/5' : ''}`}>
      <div className="flex items-center gap-4">
        {getIcon()}
        <div>
          <h4 className="font-medium text-[#e9edef]">{step.title}</h4>
          <span className="text-xs text-[#8696a0]">Estado: {step.status}</span>
        </div>
      </div>
      <span className="font-mono text-xs text-[#00a884]">{step.duration}</span>
    </div>
  );
};

const ConsolePanel = ({ logs }) => (
  <div className="h-48 border-t border-[#202c33] bg-[#0d1418] flex flex-col">
    <div className="px-4 py-2 border-b border-[#202c33] flex justify-between items-center">
      <span className="text-xs font-medium text-[#8696a0]">Terminal</span>
      <span className="text-xs text-[#8696a0]">bash</span>
    </div>
    <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1">
      {logs.length === 0 && <span className="text-[#8696a0] italic">Esperando output...</span>}
      {logs.map((log, i) => (
        <div key={i} className="flex gap-3">
          <span className="text-[#8696a0] select-none">{log.timestamp}</span>
          <span className={
            log.type === 'error' ? 'text-red-400' : 
            log.type === 'success' ? 'text-green-400' : 'text-[#e9edef]'
          }>
            {log.message}
          </span>
        </div>
      ))}
    </div>
  </div>
);

const MetricCard = ({ title, value, icon, color }) => (
  <div className="bg-[#111b21] p-6 rounded-xl border border-[#202c33] flex items-center justify-between">
    <div>
      <p className="text-[#8696a0] text-sm mb-1">{title}</p>
      <h3 className="text-2xl font-light text-[#e9edef]">{value}</h3>
    </div>
    <div className={`${color} p-3 rounded-lg bg-[#202c33]/50`}>
      {icon}
    </div>
  </div>
);

const LoaderIcon = ({ className }) => (
  <svg className={`animate-spin h-4 w-4 ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

export default DeveloperView;