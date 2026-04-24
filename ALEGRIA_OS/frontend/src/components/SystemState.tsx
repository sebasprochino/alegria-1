import React from 'react';
import { Shield, Zap, HelpCircle, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SystemStateProps {
  status: 'idle' | 'thinking' | 'doubt' | 'executing' | 'error';
}

const SystemState: React.FC<SystemStateProps> = ({ status }) => {
  const states = {
    idle: {
      label: 'Soberanía Activa',
      icon: <CheckCircle2 className="w-3 h-3 text-emerald-500" />,
      color: 'text-emerald-500/80',
      bg: 'bg-emerald-500/5'
    },
    thinking: {
      label: 'Analizando Intención',
      icon: <Activity className="w-3 h-3 text-blue-400 animate-pulse" />,
      color: 'text-blue-400',
      bg: 'bg-blue-400/5'
    },
    doubt: {
      label: 'Estado de Duda (ACSP)',
      icon: <HelpCircle className="w-3 h-3 text-amber-500 animate-bounce" />,
      color: 'text-amber-500',
      bg: 'bg-amber-500/5'
    },
    executing: {
      label: 'Ejecutando Mandato',
      icon: <Zap className="w-3 h-3 text-purple-400 animate-spin-slow" />,
      color: 'text-purple-400',
      bg: 'bg-purple-400/5'
    },
    error: {
      label: 'Fallo de Protocolo',
      icon: <AlertTriangle className="w-3 h-3 text-red-500" />,
      color: 'text-red-500',
      bg: 'bg-red-500/5'
    }
  };

  const current = states[status] || states.idle;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/5 ${current.bg} transition-all duration-500`}>
      <div className="flex items-center justify-center">
        {current.icon}
      </div>
      <span className={`text-[9px] font-bold uppercase tracking-widest ${current.color}`}>
        {current.label}
      </span>
      <div className="ml-1 flex items-center gap-0.5">
        <Shield size={8} className="text-white/20" />
      </div>
    </div>
  );
};

export default SystemState;
