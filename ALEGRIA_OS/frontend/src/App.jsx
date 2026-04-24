import React, { useState, useEffect, useRef, Suspense, lazy } from 'react';
import {
  MoreVertical, Search as SearchIcon, ArrowLeft, Mic,
  Bell, ChevronRight, X as XIcon
} from 'lucide-react';

// --- Mensajes Proactivos de Agentes (Pantalla Inicial) ---
const PROACTIVE_HOME_ALERTS = [
  {
    id: 'radar-01',
    agent: 'Radar',
    agentColor: '#38bdf8',
    dotColor: '#38bdf8',
    message: 'Ha detectado 3 nuevas oportunidades en nichos de marca emergentes.',
    action: 'Ver análisis',
    targetId: 'radar',
  },
  {
    id: 'veo-01',
    agent: 'Veoscanner',
    agentColor: '#a78bfa',
    dotColor: '#a78bfa',
    message: 'Completó el escaneo visual. Semillas listas para gestión de identidad.',
    action: 'Ver semillas',
    targetId: 'veoscope',
  },
  {
    id: 'nexus-01',
    agent: 'Nexus',
    agentColor: '#34d399',
    dotColor: '#34d399',
    message: 'Memoria cruzada actualizada. Se añadieron 7 vectores de identidad de marca.',
    action: 'Inspeccionar',
    targetId: 'nexus_prime',
  },
  {
    id: 'anima-01',
    agent: 'Anima',
    agentColor: '#f472b6',
    dotColor: '#f472b6',
    message: 'El proyecto Chordata tiene coherencia alta. Listo para fase de expansión.',
    action: 'Continuar',
    targetId: 'genesis',
  },
];
import { initializeRegistry } from './core/initializeRegistry';
import { adaptBackendResponse, adaptNetworkError } from './utils/messageAdapter';
import SystemState from './components/SystemState';
import { categories } from './components/sidebarCategories';
import SidebarComp from './components/SidebarComp';
const AnimaUI = lazy(() => import('./anima/AnimaUI'));
const DynamicWorkspace = lazy(() => import('./components/DynamicWorkspace'));
const RadarDashboard = lazy(() => import('./radar/RadarDashboard'));
const GenesisUI = lazy(() => import('./genesis/GenesisUI'));
const BrandScannerUI = lazy(() => import('./brand/BrandScannerUI'));
const BrandStudioUI = lazy(() => import('./brand/BrandStudioUI'));
const ContentMachineUI = lazy(() => import('./content/ContentMachineUI'));
const VEOscopeUI = lazy(() => import('./veoscanner/VEOscopeUI'));
const SettingsUI = lazy(() => import('./system/SettingsUI'));
const LexiconPanel = lazy(() => import('./lexicon/LexiconPanel'));
const NexusPrimeUI = lazy(() => import('./nexus/NexusPrimeUI'));
const DevAgentUI = lazy(() => import('./developer/DevAgentUI'));
const MandoUI = lazy(() => import('./mando/MandoUI'));
const VideoAIHubUI = lazy(() => import('./components/VideoAIHubUI'));
const TallerUI = lazy(() => import('./components/TallerUI'));
const AnimaForgeUI = lazy(() => import('./components/AnimaForgeUI'));
const NoticiasUI = lazy(() => import('./components/NoticiasUI'));
const CRMUI = lazy(() => import('./components/CRMUI'));
const AppAgentUI = lazy(() => import('./components/AppAgentUI'));
const MarketplaceUI = lazy(() => import('./components/MarketplaceUI'));
const APIInstallerUI = lazy(() => import('./components/APIInstallerUI'));
const NexusUI = lazy(() => import('./components/NexusUI'));
import ExternalToolsPanel from './components/ExternalToolsPanel';
import ChatModuleMobile from './components/ChatModuleMobile';
import AlegrIAIcon from './components/AlegrIAIcon';

import { ErrorBoundary } from './components/ErrorBoundary';

// --- Minimal fallback for Suspense boundaries ---
const ModuleFallback = () => (
  <div className="flex-1 h-full flex items-center justify-center bg-[#0b141a]">
    <div className="flex flex-col items-center gap-3">
      <div className="w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-400 animate-spin" />
      <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Cargando módulo…</span>
    </div>
  </div>
);

// --- COMPONENTE PRINCIPAL ---

const App = () => {
  const [selectedChat, setSelectedChat] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [messages, setMessages] = useState({});
  const [inputText, setInputText] = useState('');
  const [provider, setProvider] = useState('ollama'); // ⚡ 'ollama' (Local) o 'cascada' (Cloud Failover)
  const [systemStatus, setSystemStatus] = useState('idle'); // 🛡️ ACSP Status: idle, thinking, doubt, executing, error
  const [isToolPanelOpen, setIsToolPanelOpen] = useState(false);
  const [isMobileChatOpen, setIsMobileChatOpen] = useState(false);

  // --- Estado de Alertas Proactivas (Pantalla Inicial) ---
  const [homeAlertIndex, setHomeAlertIndex] = useState(0);
  const [homeAlertVisible, setHomeAlertVisible] = useState(true);
  const [dismissedHomeAlerts, setDismissedHomeAlerts] = useState(new Set());
  const homeAlertTimer = useRef(null);

  const activeHomeAlerts = PROACTIVE_HOME_ALERTS.filter(a => !dismissedHomeAlerts.has(a.id));
  const currentHomeAlert = activeHomeAlerts[homeAlertIndex % Math.max(activeHomeAlerts.length, 1)];

  useEffect(() => {
    if (selectedChat || activeHomeAlerts.length <= 1) return;
    homeAlertTimer.current = setInterval(() => {
      setHomeAlertVisible(false);
      setTimeout(() => {
        setHomeAlertIndex(prev => (prev + 1) % activeHomeAlerts.length);
        setHomeAlertVisible(true);
      }, 350);
    }, 5000);
    return () => clearInterval(homeAlertTimer.current);
  }, [selectedChat, activeHomeAlerts.length]);

  const handleDismissHomeAlert = (id) => {
    setHomeAlertVisible(false);
    setTimeout(() => {
      setDismissedHomeAlerts(prev => new Set([...prev, id]));
      setHomeAlertIndex(0);
      setHomeAlertVisible(true);
    }, 300);
  };

  const handleHomeAlertAction = (alert) => {
    const target = categories.flatMap(c => c.items).find(i => i.id === alert.targetId);
    if (target) setSelectedChat(target);
  };

  useEffect(() => {
    initializeRegistry();
  }, []);

  // --- EFECTO: Saludo Proactivo (ACSP Controlled Proactivity) ---
  useEffect(() => {
    if (selectedChat && (!messages[selectedChat.id] || messages[selectedChat.id].length === 0)) {
       // Solo en módulos conversacionales
       const convoModules = ['genesis', 'brand_scanner', 'veoscope', 'content', 'anima_chat'];
       if (convoModules.includes(selectedChat.id)) {
          const triggerProactive = async () => {
             try {
                const res = await fetch('/api/anima/proactive', { method: 'POST' });
                if (res.ok) {
                   const data = await res.json();
                   if (data.status === "Authorized" || data.insight) {
                      const adapted = adaptBackendResponse(data);
                      const animaMsg = {
                        ...adapted,
                        id: crypto.randomUUID(),
                        role: 'anima',
                        content: adapted.content,
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      };
                      setMessages(prev => ({ ...prev, [selectedChat.id]: [animaMsg] }));
                   }
                } else {
                   const errorText = await res.text();
                   console.warn(`[PROACTIVE] Server returned ${res.status}:`, errorText);
                }
             } catch (e) {
                console.warn("⚠️ [PROACTIVE] No se pudo obtener saludo inicial:", e);
             }
          };
          triggerProactive();
       }
    }
  }, [selectedChat, messages]);


  /**
   * handleExecuteCommand
   * Ejecuta un mandato autorizado por el operador (paso 2 del protocolo ACSP).
   */
  const handleExecuteCommand = React.useCallback(async (intent, optionId, intentionId) => {
    if (!selectedChat) return;
    const chatID = selectedChat.id;

    try {
      setSystemStatus('executing');
      const resp = await fetch(`/api/anima/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          intent, 
          option_id: optionId,
          intention_id: intentionId 
        })
      });
      
      if (!resp.ok) {
        const errorText = await resp.text();
        throw new Error(`Error en ejecución (${resp.status}): ${errorText}`);
      }

      const data = await resp.json();
      setSystemStatus('idle');
      const adapted = adaptBackendResponse(data);

      const animaMsg = {
        ...adapted,
        id: crypto.randomUUID(),
        role: 'anima',
        content: adapted.content,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => ({ ...prev, [chatID]: [...(prev[chatID] || []), animaMsg] }));
    } catch (error) {
      console.error("Error en ejecución de mandato:", error);
      setSystemStatus('idle');
    }
  }, [selectedChat]);

  const handleSendMessage = React.useCallback(async (textOverride, metadata = null) => {
    const textToSend = typeof textOverride === 'string' ? textOverride : inputText;
    if (!textToSend.trim() || !selectedChat) return;

    const chatID = selectedChat.id;
    const userMsg = { 
      id: crypto.randomUUID(), 
      role: 'user', 
      content: textToSend, 
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      metadata: metadata
    };
    
    setMessages(prev => ({ ...prev, [chatID]: [...(prev[chatID] || []), userMsg] }));
    if (typeof textOverride !== 'string') setInputText('');
    setSystemStatus('thinking');

    let resp;
    try {
      resp = await fetch(`/api/anima/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content: textToSend,
          provider: provider, // ⚡ Cascada activa
          file_metadata: metadata
        })
      });

      if (!resp.ok) {
        const errorText = await resp.text();
        throw new Error(`Connection error (${resp.status}): ${errorText.substring(0, 50)}...`);
      }

      const data = await resp.json();
      
      const adapted = adaptBackendResponse(data);
      
      // --- CRITERIO DE INTENCIÓN (Auto-execute) ---
      if (adapted.autoExecute) {
        setSystemStatus('executing');
        console.log("⚡ [ACSP] Auto-ejecución autorizada. Despachando mandato...");
        return await handleExecuteCommand(textToSend, "execute_direct");
      }

      if (adapted.mode === 'conversation') {
        setSystemStatus('idle');
      } else if (adapted.type === 'strategy') {
        setSystemStatus('doubt');
      } else {
        setSystemStatus('idle');
      }

      const animaMsg = {
        ...adapted,
        id: crypto.randomUUID(),
        role: 'anima',
        content: adapted.content,
        mode: adapted.meta?.mode || adapted.mode,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => ({ ...prev, [chatID]: [...(prev[chatID] || []), animaMsg] }));
    } catch (error) {
      console.error("Error en el despacho ACSP:", error);
      const errorAdapted = await adaptNetworkError(error, resp);
      const errorMsg = {
        ...errorAdapted,
        id: crypto.randomUUID(),
        role: 'anima',
        content: errorAdapted.content,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => ({ ...prev, [chatID]: [...(prev[chatID] || []), errorMsg] }));
    }
  }, [inputText, selectedChat, provider, handleExecuteCommand]);

  const executeOption = React.useCallback((optionId, intentionIdInput) => {
    if (typeof optionId === 'string' && optionId.startsWith('/')) {
      const mode = optionId.substring(1);
      if (mode === 'investigacion') {
         const radarNode = categories.flatMap(c => c.items).find(i => i.id === 'radar');
         if (radarNode) setSelectedChat(radarNode);
      }
      return;
    }

    const chatID = selectedChat?.id;
    const chatMsgs = messages[chatID] || [];
    
    // Buscar el mensaje de tipo 'strategy' que originó esto para obtener su intention_id
    const decisionMsg = [...chatMsgs].reverse().find(m => m.type === 'strategy');
    const finalIntentionId = intentionIdInput || decisionMsg?.meta?.intentionId || decisionMsg?.intentionId;

    // Buscar el último mensaje del usuario para obtener el "intent" original
    const lastUserMsg = [...chatMsgs].reverse().find(m => m.role === 'user');
    
    if (lastUserMsg) {
      handleExecuteCommand(lastUserMsg.content, optionId, finalIntentionId);
    }
  }, [selectedChat, messages, handleExecuteCommand]);

  return (
    <ErrorBoundary>
      <div className="flex bg-[#F9FAFB] text-slate-900 h-screen font-sans antialiased selection:bg-purple-500/10 tracking-tight transition-colors duration-700 overflow-hidden">
      {/* Sidebar deferred — does NOT block LCP */}
      <Suspense fallback={<div className="w-20 h-full bg-[#1E293B] border-r border-white/5 flex-shrink-0" />}>
        <SidebarComp 
          selectedChat={selectedChat} 
          setSelectedChat={setSelectedChat} 
          isSidebarOpen={isSidebarOpen} 
          setIsSidebarOpen={setIsSidebarOpen} 
          provider={provider}
          setProvider={setProvider}
          onOpenTools={() => setIsToolPanelOpen(true)}
        />
      </Suspense>
      
      <main className={`flex-1 flex flex-col relative h-full transition-all duration-300 ${!selectedChat ? 'hidden md:flex' : 'flex'}`}>
        {!selectedChat ? (
          // *** LCP ELEMENT — rendered inline, zero dependency on lazy chunks ***
          // *** LCP ELEMENT — Ingeniería Operativa ***
          <div className="flex-1 flex flex-col items-center justify-center px-12 pt-10 pb-6 text-center bg-white relative overflow-hidden">
             {/* Fondo premium con gradientes suaves */}
             <div className="absolute top-0 left-0 w-full h-full opacity-30 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-purple-100 blur-[140px] rounded-full animate-pulse" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-blue-100 blur-[140px] rounded-full animate-pulse" style={{ animationDelay: '3s' }} />
             </div>

             <div className="relative group mb-14">
                {/* Resplandor de fondo */}
                <div className="absolute inset-0 bg-white blur-3xl rounded-full scale-150 transition-all duration-700"></div>
                <div className="relative w-48 h-48 bg-white rounded-[48px] flex items-center justify-center shadow-[0_20px_50px_rgba(0,0,0,0.04)] border border-white group-hover:scale-105 transition-all duration-700">
                   <AlegrIAIcon size={120} className="relative z-10" />
                </div>
             </div>

             <h2 className="text-6xl font-black text-black mb-4 tracking-[-0.08em] uppercase">ALEGR-IA OS</h2>
             <p className="max-w-md text-slate-400 text-[14px] leading-relaxed mb-8 font-light tracking-wide uppercase">
               Sovereign Command Center <br/>
               <span className="text-purple-500 font-bold tracking-[0.3em] text-[10px]">Nexus Prime Active</span>
             </p>

             {/* ── COMUNICACIÓN PROACTIVA — Pantalla Inicial ── */}
             {activeHomeAlerts.length > 0 && currentHomeAlert && (
               <div
                 className="w-full max-w-sm mb-8"
                 style={{
                   opacity: homeAlertVisible ? 1 : 0,
                   transform: homeAlertVisible ? 'translateY(0)' : 'translateY(8px)',
                   transition: 'opacity 0.35s ease, transform 0.35s ease',
                 }}
               >
                 <div className="flex items-start gap-3 bg-slate-50 border border-slate-200/80 rounded-2xl px-4 py-3 text-left shadow-sm">
                   {/* Agent badge */}
                   <div className="flex items-center gap-1.5 pt-0.5 shrink-0">
                     <Bell size={12} style={{ color: currentHomeAlert.agentColor }} />
                     <span
                       className="text-[10px] font-black uppercase tracking-widest"
                       style={{ color: currentHomeAlert.agentColor }}
                     >
                       {currentHomeAlert.agent}
                     </span>
                     <span
                       className="w-1.5 h-1.5 rounded-full animate-pulse"
                       style={{ backgroundColor: currentHomeAlert.dotColor }}
                     />
                   </div>

                   {/* Message */}
                   <p className="flex-1 text-[11px] text-slate-500 leading-relaxed">
                     {currentHomeAlert.message}
                   </p>

                   {/* Actions */}
                   <div className="flex items-center gap-1 shrink-0">
                     {currentHomeAlert.action && (
                       <button
                         onClick={() => handleHomeAlertAction(currentHomeAlert)}
                         className="text-[10px] font-black uppercase tracking-wider flex items-center gap-0.5 transition-colors hover:opacity-70"
                         style={{ color: currentHomeAlert.agentColor }}
                         aria-label={currentHomeAlert.action}
                       >
                         {currentHomeAlert.action}
                         <ChevronRight size={9} />
                       </button>
                     )}
                     <button
                       onClick={() => handleDismissHomeAlert(currentHomeAlert.id)}
                       className="ml-1.5 text-slate-300 hover:text-slate-500 transition-colors"
                       aria-label="Descartar alerta"
                       title="Descartar"
                     >
                       <XIcon size={12} />
                     </button>
                   </div>
                 </div>

                 {/* Pagination dots */}
                 {activeHomeAlerts.length > 1 && (
                   <div className="flex justify-center gap-1.5 mt-2">
                     {activeHomeAlerts.map((_, i) => (
                       <button
                         key={i}
                         aria-label={`Alerta ${i + 1}`}
                         onClick={() => {
                           setHomeAlertVisible(false);
                           setTimeout(() => { setHomeAlertIndex(i); setHomeAlertVisible(true); }, 300);
                         }}
                         className="h-1 rounded-full transition-all duration-300"
                         style={{
                           width: i === homeAlertIndex % activeHomeAlerts.length ? '16px' : '4px',
                           backgroundColor: i === homeAlertIndex % activeHomeAlerts.length ? '#7c3aed' : '#d1d5db',
                         }}
                       />
                     ))}
                   </div>
                 )}
               </div>
             )}

             <div className="flex items-center gap-4">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-[10px] text-slate-300 font-mono tracking-widest">127.0.0.1 // SECURE_CONNECTION</span>
             </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col h-full overflow-hidden animate-fade-in shadow-2xl">
              {/* Hide default header for modules with custom headers like Radar or Noticias */}
              {!['radar', 'noticias', 'brand_studio'].includes(selectedChat.id) && (
                <div className="p-4 bg-[#1f2c34] flex items-center justify-between border-b border-white/5 z-20">
                <div className="flex items-center gap-4">
                  <button 
                    className="md:hidden text-gray-400" 
                    onClick={() => setSelectedChat(null)}
                    aria-label="Volver al inicio"
                    title="Volver al inicio"
                  >
                     <ArrowLeft size={24} />
                  </button>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center border shadow-glow-sm transition-all ${
                    provider === 'ollama' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' : 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                  }`}>
                    {selectedChat.icon}
                  </div>
                  <div className="flex flex-col">
                    <h2 className="text-base md:text-sm font-bold text-white font-premium tracking-tight">{selectedChat.name}</h2>
                    <span className={`text-[12px] md:text-[10px] font-bold uppercase tracking-tighter ${provider === 'ollama' ? 'text-orange-400' : 'text-purple-400'}`}>
                      {provider === 'ollama' ? 'Soberanía Local' : 'Casacada Cloud'}
                    </span>
                  </div>
                </div>
                
                <div className="hidden lg:block absolute left-1/2 -translate-x-1/2">
                   <SystemState status={systemStatus} />
                </div>

                <div className="flex items-center gap-4 text-gray-400">
                   <SearchIcon 
                     size={20} 
                     className="hover:text-white cursor-pointer transition-colors" 
                     aria-label="Buscar"
                     role="button"
                   />
                   <MoreVertical 
                     size={20} 
                     className="hover:text-white cursor-pointer transition-colors" 
                     aria-label="Más opciones"
                     role="button"
                   />
                </div>
              </div>
            )}

              <div className="flex-1 overflow-hidden relative">
                {/* === MÓDULOS: each lazy-loaded, isolated Suspense boundary === */}
                <Suspense fallback={<ModuleFallback />}>
                  {selectedChat.id === 'genesis' ? (
                    (messages[selectedChat.id] && messages[selectedChat.id].length > 0) ? (
                      <AnimaUI 
                        agent={selectedChat} 
                        messages={messages[selectedChat.id] || []}
                        onSendMessage={handleSendMessage}
                        onExecuteOption={executeOption}
                        onBack={() => setSelectedChat(null)}
                      />
                    ) : (
                      <GenesisUI onBack={() => setSelectedChat(null)} onSendMessage={handleSendMessage} />
                    )
                  ) : selectedChat.id === 'brand_scanner' ? (
                    <BrandScannerUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'veoscope' ? (
                    <VEOscopeUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'content' ? (
                    (messages[selectedChat.id] && messages[selectedChat.id].length > 0) ? (
                      <AnimaUI 
                        agent={selectedChat} 
                        messages={messages[selectedChat.id] || []}
                        onSendMessage={handleSendMessage}
                        onExecuteOption={executeOption}
                        onBack={() => setSelectedChat(null)}
                      />
                    ) : (
                      <ContentMachineUI onBack={() => setSelectedChat(null)} />
                    )
                  ) : selectedChat.id === 'brand_studio' ? (
                    <BrandStudioUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'radar' ? (
                    <RadarDashboard onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'settings' ? (
                    <SettingsUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'nexus_prime' ? (
                    <NexusPrimeUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'developer' ? (
                    <DevAgentUI />
                  ) : selectedChat.id === 'mando' ? (
                    <MandoUI 
                      onBack={() => setSelectedChat(null)} 
                      onSendMessage={handleSendMessage} 
                      onNavigate={(id) => {
                        const target = categories.flatMap(c => c.items).find(item => item.id === id);
                        if (target) setSelectedChat(target);
                      }}
                    />
                  ) : selectedChat.id === 'video_hub' ? (
                    <VideoAIHubUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'taller' ? (
                    <TallerUI onBack={() => setSelectedChat(null)} agent={selectedChat} />
                  ) : selectedChat.id === 'anima_forge' ? (
                    <AnimaForgeUI onBack={() => setSelectedChat(null)} />
                  ) : selectedChat.id === 'noticias' ? (
                    <NoticiasUI />
                  ) : selectedChat.id === 'crm' ? (
                    <CRMUI />
                  ) : selectedChat.id === 'app_agent' ? (
                    <AppAgentUI />
                  ) : selectedChat.id === 'marketplace' ? (
                    <MarketplaceUI />
                  ) : selectedChat.id === 'api_installer' ? (
                    <APIInstallerUI />
                  ) : selectedChat.id === 'nexus' ? (
                    <NexusUI onBack={() => setSelectedChat(null)} />
                  ) : (
                    <AnimaUI 
                      agent={selectedChat} 
                      messages={messages[selectedChat.id] || []}
                      onSendMessage={handleSendMessage}
                      onExecuteOption={executeOption}
                      onBack={() => setSelectedChat(null)}
                    />
                  )}
                </Suspense>
              </div>
          </div>
        )}
      </main>
      
      {/* Lexicon Observer Lateral — lazy, non-critical */}
      {selectedChat && !['settings', 'nexus_prime', 'radar'].includes(selectedChat.id) && (
        <Suspense fallback={null}>
          <LexiconPanel messages={messages[selectedChat.id] || []} />
        </Suspense>
      )}

      {/* BOTÓN FLOTANTE MÓVIL (Trigger de Diálogo) */}
      <div className="md:hidden fixed bottom-6 right-6 z-[150]">
        <button 
          onClick={() => setIsMobileChatOpen(true)}
          className="w-14 h-14 bg-black text-white rounded-full flex items-center justify-center shadow-2xl active:scale-95 transition-transform"
        >
          <Mic size={24} />
        </button>
      </div>

      {/* MÓDULO DE CHAT MÓVIL (Expansión Circular) */}
      {isMobileChatOpen && (
        <ChatModuleMobile 
          isOpen={isMobileChatOpen}
          onClose={() => setIsMobileChatOpen(false)}
          messages={selectedChat ? (messages[selectedChat.id] || []) : []}
          onSend={(text) => handleSendMessage(text)}
        />
      )}

      {/* Acelerador Cognitivo (WebViews) */}
      <ExternalToolsPanel 
        isOpen={isToolPanelOpen} 
        onClose={() => setIsToolPanelOpen(false)} 
      />
      </div>
    </ErrorBoundary>
  );
};

export default App;
