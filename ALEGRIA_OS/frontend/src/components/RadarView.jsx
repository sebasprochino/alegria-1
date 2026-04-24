import React from 'react';
import { Radio, Globe, Wifi, ShieldAlert } from 'lucide-react';

const RadarView = () => {
  return (
    <div className="flex flex-col h-full bg-[#0b141a] items-center justify-center p-8 text-center">
      <div className="w-32 h-32 rounded-full border-2 border-[#00a884] flex items-center justify-center relative mb-6">
         <div className="absolute w-full h-full rounded-full border border-[#00a884]/30 animate-ping"></div>
         <Radio size={48} className="text-[#00a884]" />
      </div>
      <h2 className="text-2xl font-light text-[#e9edef] mb-2">Sistemas de Radar Activos</h2>
      <p className="text-[#8696a0] max-w-md mx-auto mb-8">
        Escaneando el entorno digital en busca de nueva información y actualizaciones de contexto relevantes para el Creador.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl">
        <div className="bg-[#111b21] p-4 rounded-lg border border-[#222d34] flex flex-col items-center gap-2">
           <Globe className="text-blue-400" />
           <span className="text-[#e9edef] text-sm font-medium">World Gateway</span>
           <span className="text-[#8696a0] text-xs">Conectado</span>
        </div>
        <div className="bg-[#111b21] p-4 rounded-lg border border-[#222d34] flex flex-col items-center gap-2">
           <Wifi className="text-green-400" />
           <span className="text-[#e9edef] text-sm font-medium">Feed de Datos</span>
           <span className="text-[#8696a0] text-xs">Estable</span>
        </div>
        <div className="bg-[#111b21] p-4 rounded-lg border border-[#222d34] flex flex-col items-center gap-2">
           <ShieldAlert className="text-yellow-400" />
           <span className="text-[#e9edef] text-sm font-medium">Filtro Ético</span>
           <span className="text-[#8696a0] text-xs">Vigilante</span>
        </div>
      </div>
    </div>
  );
};

export default RadarView;