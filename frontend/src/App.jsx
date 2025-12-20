import { useState, useEffect, useRef } from "react";
import {
  Send,
  Settings,
  Radio,
  MessageSquare,
  Zap,
  Plus,
  Check,
  X,
  Loader2,
  Volume2,
  VolumeX,
  ChevronDown,
  ExternalLink,
  Server,
  Key,
  Cpu,
} from "lucide-react";

const API_URL = "http://localhost:8000";

// Hook para voz
const useVoice = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);

  const speak = (text) => {
    if (!voiceEnabled || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "es-AR";
    u.rate = 0.9;
    u.pitch = 1.0;
    u.onstart = () => setIsSpeaking(true);
    u.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(u);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return { speak, stop, isSpeaking, voiceEnabled, setVoiceEnabled };
};

export default function App() {
  // Estado principal
  const [view, setView] = useState("chat");
  const [systemStatus, setSystemStatus] = useState(null);

  // Chat
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { speak, voiceEnabled, setVoiceEnabled } = useVoice();

  // Proveedores
  const [availableProviders, setAvailableProviders] = useState([]);
  const [configuredProviders, setConfiguredProviders] = useState([]);
  const [activeProvider, setActiveProvider] = useState(null);
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [selectedModel, setSelectedModel] = useState("");

  // Cargar estado inicial
  useEffect(() => {
    fetchSystemStatus();
    fetchProviders();
    fetchActiveProvider();
  }, []);

  // Scroll automático en chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSystemStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/system/status`);
      setSystemStatus(await res.json());
    } catch {
      setSystemStatus({ error: "Sistema no disponible" });
    }
  };

  const fetchProviders = async () => {
    try {
      // Proveedores disponibles via RADAR
      const radarRes = await fetch(`${API_URL}/radar/providers`);
      const radarData = await radarRes.json();
      setAvailableProviders(radarData.providers || []);

      // Proveedores configurados
      const configRes = await fetch(`${API_URL}/providers`);
      const configData = await configRes.json();
      setConfiguredProviders(configData.providers || []);
    } catch (e) {
      console.error("Error fetching providers:", e);
    }
  };

  const fetchActiveProvider = async () => {
    try {
      const res = await fetch(`${API_URL}/providers/active`);
      const data = await res.json();
      setActiveProvider(data.active);
    } catch {
      setActiveProvider(null);
    }
  };

  const handleAddProvider = async () => {
    if (!selectedProvider || !apiKeyInput.trim()) return;

    try {
      const res = await fetch(`${API_URL}/providers/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: selectedProvider.name,
          api_key: apiKeyInput,
          model: selectedModel || selectedProvider.models?.[0],
        }),
      });

      if (res.ok) {
        setShowAddProvider(false);
        setApiKeyInput("");
        setSelectedProvider(null);
        setSelectedModel("");
        fetchProviders();
        fetchActiveProvider();
      }
    } catch (e) {
      console.error("Error adding provider:", e);
    }
  };

  const handleSelectProvider = async (providerName, model = null) => {
    try {
      await fetch(`${API_URL}/providers/select`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: providerName, model }),
      });
      fetchActiveProvider();
    } catch (e) {
      console.error("Error selecting provider:", e);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content }),
      });

      const data = await res.json();
      const reply = data.reply || "Sin respuesta";

      setMessages((m) => [
        ...m,
        {
          role: "anima",
          content: reply,
          provider: data.provider,
          model: data.model,
        },
      ]);

      speak(reply);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "anima", content: "Error de conexión con el servidor." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // ============ RENDER ============

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">A</div>
            <span className="logo-text">ALEGR-IA</span>
          </div>
          <span className="version-badge">Soberano</span>
        </div>

        <nav className="nav-menu">
          <button
            className={`nav-item ${view === "chat" ? "active" : ""}`}
            onClick={() => setView("chat")}
          >
            <MessageSquare size={20} />
            <span>Chat</span>
          </button>
          <button
            className={`nav-item ${view === "providers" ? "active" : ""}`}
            onClick={() => setView("providers")}
          >
            <Cpu size={20} />
            <span>Proveedores</span>
          </button>
          <button
            className={`nav-item ${view === "radar" ? "active" : ""}`}
            onClick={() => setView("radar")}
          >
            <Radio size={20} />
            <span>RADAR</span>
          </button>
        </nav>

        {/* Provider Status */}
        <div className="provider-status">
          {activeProvider ? (
            <div className="active-provider">
              <Zap size={14} className="text-green" />
              <div>
                <div className="provider-name">{activeProvider.provider}</div>
                <div className="provider-model">{activeProvider.model || "default"}</div>
              </div>
            </div>
          ) : (
            <div className="no-provider">
              <X size={14} />
              <span>Sin proveedor</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* === CHAT VIEW === */}
        {view === "chat" && (
          <div className="chat-container">
            <div className="chat-header">
              <h1>Anima Chordata</h1>
              <div className="chat-controls">
                <button
                  className={`icon-btn ${voiceEnabled ? "active" : ""}`}
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  title={voiceEnabled ? "Desactivar voz" : "Activar voz"}
                >
                  {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
                </button>
              </div>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-chat">
                  <div className="empty-icon">🧠</div>
                  <h2>Hola, soy Anima</h2>
                  <p>
                    {activeProvider
                      ? `Usando ${activeProvider.provider}. ¿En qué te ayudo?`
                      : "Configura un proveedor en la sección Proveedores para comenzar."}
                  </p>
                </div>
              ) : (
                messages.map((m, i) => (
                  <div key={i} className={`message ${m.role}`}>
                    <div className="message-content">{m.content}</div>
                    {m.provider && (
                      <div className="message-meta">
                        vía {m.provider} {m.model && `• ${m.model}`}
                      </div>
                    )}
                  </div>
                ))
              )}
              {isLoading && (
                <div className="message anima loading">
                  <Loader2 className="spin" size={20} />
                  <span>Anima está pensando...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="input-container">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder={
                  activeProvider
                    ? "Escribí tu mensaje..."
                    : "Configurá un proveedor primero..."
                }
                disabled={!activeProvider || isLoading}
              />
              <button
                className="send-btn"
                onClick={handleSend}
                disabled={!activeProvider || isLoading || !input.trim()}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        )}

        {/* === PROVIDERS VIEW === */}
        {view === "providers" && (
          <div className="providers-container">
            <div className="section-header">
              <h1>Proveedores LLM</h1>
              <button className="btn-primary" onClick={() => setShowAddProvider(true)}>
                <Plus size={18} />
                Agregar Proveedor
              </button>
            </div>

            {/* Proveedor Activo */}
            {activeProvider && (
              <div className="active-card">
                <div className="card-header">
                  <Zap className="text-green" size={20} />
                  <h2>Proveedor Activo</h2>
                </div>
                <div className="active-details">
                  <div className="detail-row">
                    <span className="label">Proveedor:</span>
                    <span className="value">{activeProvider.provider}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Modelo:</span>
                    <span className="value">{activeProvider.model || "default"}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">API Key:</span>
                    <span className="value mono">{activeProvider.api_key}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Lista de Configurados */}
            <div className="section">
              <h3>Configurados</h3>
              {configuredProviders.length === 0 ? (
                <div className="empty-state">
                  <p>No hay proveedores configurados aún.</p>
                  <p>Hacé clic en "Agregar Proveedor" para empezar.</p>
                </div>
              ) : (
                <div className="providers-grid">
                  {configuredProviders.map((p) => (
                    <div key={p.name} className={`provider-card ${p.is_active ? "active" : ""}`}>
                      <div className="card-top">
                        <Server size={24} />
                        <h4>{p.name}</h4>
                        {p.is_active && <Check className="check-icon" size={18} />}
                      </div>
                      <div className="card-info">
                        <span>{p.models?.length || 0} modelos</span>
                        {p.has_key && <Key size={14} />}
                      </div>
                      {!p.is_active && (
                        <button
                          className="btn-select"
                          onClick={() => handleSelectProvider(p.name)}
                        >
                          Activar
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Modal Agregar */}
            {showAddProvider && (
              <div className="modal-overlay" onClick={() => setShowAddProvider(false)}>
                <div className="modal" onClick={(e) => e.stopPropagation()}>
                  <div className="modal-header">
                    <h2>Agregar Proveedor</h2>
                    <button className="close-btn" onClick={() => setShowAddProvider(false)}>
                      <X size={20} />
                    </button>
                  </div>

                  <div className="modal-body">
                    {!selectedProvider ? (
                      <div className="provider-select">
                        <p>Seleccioná un proveedor:</p>
                        <div className="provider-options">
                          {availableProviders.map((p) => (
                            <button
                              key={p.name}
                              className="provider-option"
                              onClick={() => setSelectedProvider(p)}
                            >
                              <div className="option-info">
                                <h4>{p.display_name}</h4>
                                <p>{p.description}</p>
                                {p.free_tier && <span className="free-badge">Gratis</span>}
                              </div>
                              <ChevronDown size={18} className="rotate-270" />
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="api-key-form">
                        <div className="selected-header">
                          <button className="back-btn" onClick={() => setSelectedProvider(null)}>
                            ← Volver
                          </button>
                          <h3>{selectedProvider.display_name}</h3>
                        </div>

                        {selectedProvider.is_local ? (
                          <div className="local-info">
                            <p>Ollama no requiere API Key.</p>
                            <p>Asegurate de tener Ollama corriendo en localhost:11434</p>
                          </div>
                        ) : (
                          <>
                            <div className="form-group">
                              <label>API Key</label>
                              <input
                                type="password"
                                value={apiKeyInput}
                                onChange={(e) => setApiKeyInput(e.target.value)}
                                placeholder="Ingresá tu API Key..."
                              />
                              <a
                                href={selectedProvider.signup_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="signup-link"
                              >
                                Obtener API Key <ExternalLink size={14} />
                              </a>
                            </div>
                          </>
                        )}

                        <div className="form-group">
                          <label>Modelo</label>
                          <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                          >
                            <option value="">Seleccionar modelo...</option>
                            {selectedProvider.models?.map((m) => (
                              <option key={m} value={m}>
                                {m}
                              </option>
                            ))}
                          </select>
                        </div>

                        <button
                          className="btn-primary full-width"
                          onClick={handleAddProvider}
                          disabled={
                            !selectedProvider.is_local && !apiKeyInput.trim()
                          }
                        >
                          Agregar y Activar
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* === RADAR VIEW === */}
        {view === "radar" && (
          <div className="radar-container">
            <div className="section-header">
              <h1>📡 RADAR</h1>
              <p>Descubrimiento de modelos y proveedores</p>
            </div>

            <div className="radar-grid">
              {availableProviders.map((p) => (
                <div key={p.name} className="radar-card">
                  <div className="radar-card-header">
                    <h3>{p.display_name}</h3>
                    {p.free_tier && <span className="free-badge">Free Tier</span>}
                  </div>
                  <p>{p.description}</p>
                  <div className="models-list">
                    <h4>Modelos disponibles:</h4>
                    <ul>
                      {p.models?.slice(0, 4).map((m) => (
                        <li key={m}>{m}</li>
                      ))}
                      {p.models?.length > 4 && (
                        <li className="more">+{p.models.length - 4} más</li>
                      )}
                    </ul>
                  </div>
                  <a
                    href={p.signup_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="radar-link"
                  >
                    Ir al sitio <ExternalLink size={14} />
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
