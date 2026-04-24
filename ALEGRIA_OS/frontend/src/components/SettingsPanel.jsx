import React from 'react';
import { Settings, User, Lock, Moon, Bell } from 'lucide-react';

const SettingItem = ({ icon, title, description, toggle }) => (
  <div className="flex items-center justify-between p-4 border-b border-[#222d34] last:border-0 hover:bg-[#202c33]/30 transition-colors">
    <div className="flex items-center gap-4">
      <div className="text-[#8696a0]">{icon}</div>
      <div>
        <h4 className="text-[#e9edef] text-sm font-medium">{title}</h4>
        <p className="text-[#8696a0] text-xs">{description}</p>
      </div>
    </div>
    {toggle && (
      <div className="w-10 h-5 bg-[#00a884] rounded-full relative cursor-pointer">
        <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full shadow-sm"></div>
      </div>
    )}
  </div>
);

const SettingsPanel = () => {
  return (
    <div className="flex flex-col h-full bg-[#0b141a]">
      <header className="h-[60px] bg-[#111b21] px-6 flex items-center border-b border-[#222d34]">
        <h2 className="text-xl font-light text-[#e9edef] flex items-center gap-2">
          <Settings className="text-[#8696a0]" size={20} />
          Configuración del Sistema
        </h2>
      </header>

      <div className="p-6 max-w-3xl mx-auto w-full">
        <div className="bg-[#111b21] rounded-xl border border-[#222d34] overflow-hidden">
          <SettingItem 
            icon={<User size={20} />}
            title="Perfil de Usuario"
            description="Gestiona tu identidad y preferencias personales."
          />
          <SettingItem 
            icon={<Lock size={20} />}
            title="Privacidad y Seguridad"
            description="Controla el acceso a tus datos y claves API."
          />
          <SettingItem 
            icon={<Moon size={20} />}
            title="Tema Oscuro"
            description="Interfaz optimizada para entornos de baja luz."
            toggle={true}
          />
           <SettingItem 
            icon={<Bell size={20} />}
            title="Notificaciones de Radar"
            description="Alertas sobre nuevos hallazgos de información."
            toggle={true}
          />
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-[#8696a0] text-xs">ALEGR-IA OS v1.0.0 (Alpha)</p>
          <p className="text-[#8696a0] text-[10px] mt-1">Soberanía Digital Garantizada</p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;