import React, { useState } from 'react';
import { Heart, Globe, MessageSquare, Users, Check, ChevronDown, Sparkles } from 'lucide-react';

interface Plan {
  id: string;
  name: string;
  subtitle: string;
  price: string;
  features: string[];
  recommended?: boolean;
  buttonColor: string;
}

const PLANS: Plan[] = [
  {
    id: 'semilla',
    name: 'Semilla Digital',
    subtitle: 'Para empezar a tener presencia',
    price: '$ 45.000',
    features: [
      'Tu Tarjeta en la web',
      'Botones de contacto directo',
      'Sin pagos mensuales (Hosting Gratis)',
      'Enlace con tu nombre',
    ],
    buttonColor: 'bg-slate-700 hover:bg-slate-600',
  },
  {
    id: 'profesional',
    name: 'Profesional Conectado',
    subtitle: 'Para quienes atienden pacientes/clientes',
    price: '$ 120.000',
    features: [
      'Botón "Guardar Contacto" (Magia)',
      'Código QR para tu consultorio',
      'Diseño Premium con tu foto',
      'Que te encuentren fácil en WhatsApp',
    ],
    recommended: true,
    buttonColor: 'bg-gradient-to-r from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500',
  },
  {
    id: 'estudio',
    name: 'Estudio Digital',
    subtitle: 'Para equipos y clínicas',
    price: '$ 380.000',
    features: [
      'Todo lo anterior',
      'Tarjetas para todo el equipo',
      'Dominio .com propio',
      'Soporte prioritario',
    ],
    buttonColor: 'bg-slate-700 hover:bg-slate-600',
  },
];

export default function CRMUI() {
  const [activeRegion, setActiveRegion] = useState('Argentina');

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] h-full overflow-hidden">
      {/* Header */}
      <div className="px-8 pt-10 pb-6 border-b border-white/5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-pink-500/10 rounded-2xl flex items-center justify-center border border-pink-500/20">
              <Heart size={20} className="text-pink-500" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tight">Relaciones & Ventas</h1>
              <p className="text-slate-500 text-[11px] font-medium uppercase tracking-wider">
                Conecta con personas, no con transacciones.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
             <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 cursor-pointer hover:bg-white/10 transition-colors">
                <Globe size={14} className="text-slate-400" />
                <span className="text-[11px] font-bold text-slate-200">{activeRegion}</span>
                <ChevronDown size={14} className="text-slate-500" />
             </div>
             
             <div className="flex bg-white/5 rounded-xl p-1 border border-white/10">
                <button className="px-4 py-1.5 bg-pink-500 text-white rounded-lg text-[10px] font-black uppercase tracking-widest shadow-lg shadow-pink-500/20">Opciones</button>
                <button className="px-4 py-1.5 text-slate-400 hover:text-white transition-colors text-[10px] font-black uppercase tracking-widest">Mensajes</button>
                <button className="px-4 py-1.5 text-slate-400 hover:text-white transition-colors text-[10px] font-black uppercase tracking-widest">Contactos</button>
             </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
            {PLANS.map((plan) => (
              <div 
                key={plan.id}
                className={`relative flex flex-col bg-[#161b22] border rounded-[32px] p-8 transition-all duration-500 group ${
                  plan.recommended 
                    ? 'border-fuchsia-500/50 shadow-[0_0_40px_rgba(192,38,211,0.1)] scale-[1.02] z-10' 
                    : 'border-white/[0.06] hover:border-white/20'
                }`}
              >
                {plan.recommended && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-fuchsia-500 text-white text-[9px] font-black uppercase tracking-[0.2em] px-4 py-1 rounded-full shadow-lg shadow-fuchsia-500/30">
                    Recomendado
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                  <p className="text-[11px] text-slate-500 italic mb-6">{plan.subtitle}</p>
                  <div className="text-3xl font-black text-white tracking-tight">{plan.price}</div>
                </div>

                <div className="flex-1 space-y-4 mb-10">
                  {plan.features.map((feature, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <div className={`mt-0.5 w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${plan.recommended ? 'bg-fuchsia-500/20' : 'bg-white/5'}`}>
                        <Check size={10} className={plan.recommended ? 'text-fuchsia-400' : 'text-slate-500'} />
                      </div>
                      <span className="text-[12px] text-slate-300 font-light leading-snug">{feature}</span>
                    </div>
                  ))}
                </div>

                <button className={`w-full py-4 rounded-2xl text-[11px] font-black uppercase tracking-widest text-white transition-all shadow-xl active:scale-95 ${plan.buttonColor}`}>
                  Elegir para el Cliente
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
