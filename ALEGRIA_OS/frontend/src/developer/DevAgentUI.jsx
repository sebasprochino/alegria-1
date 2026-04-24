import { useState, useRef, useEffect, useCallback } from "react";
import { reportToAudit } from "../utils/error_helper";

const MODES = [
  { id: "chat", label: "Chat", icon: "◈" },
  { id: "review", label: "Code Review", icon: "⌥" },
  { id: "fix", label: "Bug Fix", icon: "⚑" },
  { id: "arch", label: "Arquitectura", icon: "⬡" },
  { id: "gen", label: "Generar", icon: "⌘" },
];

const STATUS_NODES = ["nexus", "provider_registry", "anima", "cascade", "ethical_guard"];

function CodeBlock({ code, lang }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div style={{ position: "relative", margin: "10px 0" }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        background: "#0d1117", padding: "6px 12px",
        borderRadius: "6px 6px 0 0", borderBottom: "1px solid #21262d"
      }}>
        <span style={{ fontSize: "11px", color: "#7d8590", fontFamily: "monospace" }}>{lang || "code"}</span>
        <button onClick={copy} style={{
          background: "none", border: "1px solid #30363d", borderRadius: "4px",
          color: copied ? "#3fb950" : "#7d8590", fontSize: "11px", padding: "2px 8px",
          cursor: "pointer", fontFamily: "monospace"
        }}>
          {copied ? "✓ copiado" : "copiar"}
        </button>
      </div>
      <pre style={{
        background: "#0d1117", margin: 0, padding: "14px",
        borderRadius: "0 0 6px 6px", overflowX: "auto",
        fontSize: "12.5px", lineHeight: 1.6, color: "#e6edf3",
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        border: "1px solid #21262d", borderTop: "none"
      }}>
        <code>{code}</code>
      </pre>
    </div>
  );
}

function SandboxTestResults({ results, semantic, confidence }) {
  if ((!results || results.length === 0) && (!semantic || semantic.length === 0)) return null;
  
  const levelColor = {
    HIGH: "#3fb950",
    MEDIUM: "#d29922",
    LOW: "#f85149"
  };

  return (
    <div style={{ marginTop: "12px", background: "#0d1117", border: "1px solid #30363d", borderRadius: "6px", padding: "12px" }}>
      {/* 📊 CONFIDENCE SCORE */}
      {confidence && (
        <div style={{ marginBottom: "16px", padding: "10px", background: "rgba(255,255,255,0.03)", borderRadius: "4px", border: `1px solid ${levelColor[confidence.level] || "#30363d"}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "11px", fontWeight: "700", color: "#8b949e", textTransform: "uppercase" }}>Confidence Score</span>
            <span style={{ fontSize: "14px", fontWeight: "800", color: levelColor[confidence.level] }}>{confidence.score}%</span>
          </div>
          <div style={{ height: "4px", background: "#21262d", borderRadius: "2px", margin: "8px 0" }}>
            <div style={{ height: "100%", width: `${confidence.score}%`, background: levelColor[confidence.level], borderRadius: "2px", transition: "width 0.5s ease" }} />
          </div>
          <div style={{ fontSize: "10px", color: levelColor[confidence.level], fontWeight: "700", textAlign: "right" }}>
            {confidence.level} RELIABILITY
          </div>
          {confidence.signals && confidence.signals.length > 0 && (
            <div style={{ marginTop: "8px", display: "flex", flexWrap: "wrap", gap: "4px" }}>
              {confidence.signals.map((s, i) => (
                <span key={i} style={{ fontSize: "9px", background: "#161b22", color: "#8b949e", padding: "1px 6px", borderRadius: "10px", border: "1px solid #30363d" }}>
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {results && results.length > 0 && (
        <>
          <div style={{ fontSize: "11px", fontWeight: "700", color: "#8b949e", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
            🧪 Validación Técnica (Sandbox)
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
            {results.map((t, idx) => (
              <div key={idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                   <span style={{ color: t.success ? "#3fb950" : "#ff7b72" }}>{t.success ? "✔" : "✘"}</span>
                   <span style={{ color: "#cdd9e5" }}>{t.test}</span>
                </div>
                <span style={{ 
                  color: t.success ? "#3fb950" : "#ff7b72", 
                  background: t.success ? "rgba(63,185,80,0.1)" : "rgba(255,123,114,0.1)",
                  padding: "1px 6px",
                  borderRadius: "4px",
                  fontSize: "10px",
                  fontWeight: "600"
                }}>
                  {t.success ? "PASS" : (t.status || "FAIL")}
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      {semantic && semantic.length > 0 && (
        <>
          <div style={{ fontSize: "11px", fontWeight: "700", color: "#f2cc60", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
            🧠 Validación Semántica
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {semantic.map((t, idx) => (
              <div key={idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                   <span style={{ color: t.success ? "#3fb950" : "#ff7b72" }}>{t.success ? "✔" : "✘"}</span>
                   <span style={{ color: "#cdd9e5" }}>{t.test}</span>
                </div>
                <span style={{ 
                  color: t.success ? "#3fb950" : "#ff7b72", 
                  background: t.success ? "rgba(63,185,80,0.1)" : "rgba(255,123,114,0.1)",
                  padding: "1px 6px",
                  borderRadius: "4px",
                  fontSize: "10px",
                  fontWeight: "600"
                }}>
                  {t.success ? "PASS" : (t.status || "FAIL")}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function renderContent(text) {
  const parts = [];
  const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", content: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: "code", lang: match[1], content: match[2].trim() });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    parts.push({ type: "text", content: text.slice(lastIndex) });
  }

  return parts.map((p, i) => {
    if (p.type === "code") return <CodeBlock key={i} code={p.content} lang={p.lang} />;
    return (
      <span key={i} style={{ whiteSpace: "pre-wrap" }}
        dangerouslySetInnerHTML={{
          __html: p.content
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/`([^`]+)`/g, '<code style="background:#1e2936;padding:2px 5px;border-radius:3px;font-family:monospace;font-size:12px;color:#79c0ff">$1</code>')
            .replace(/^(#{1,3})\s(.+)$/gm, (_, h, t) => {
              const sizes = { 1: "16px", 2: "14px", 3: "13px" };
              const s = sizes[h.length] || "13px";
              return `<div style="font-size:${s};font-weight:700;color:#e6edf3;margin:14px 0 6px">${t}</div>`;
            })
            .replace(/^[-•]\s(.+)$/gm, '<div style="padding-left:16px;margin:3px 0">· $1</div>')
            .replace(/^(\d+)\.\s(.+)$/gm, '<div style="padding-left:16px;margin:3px 0;color:#8b949e">$1. $2</div>')
        }}
      />
    );
  });
}

export default function DevAgentUI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("chat");
  const [history, setHistory] = useState([]);
  const [nodeStatus, setNodeStatus] = useState({});
  const [lastProvider, setLastProvider] = useState(null);
  const bottomRef = useRef(null);

  // Fetch real node status on mount
  useEffect(() => {
    fetch("/api/status")
      .then(r => r.json())
      .then(data => {
        if (data.nodes) setNodeStatus(data.nodes);
      })
      .catch(() => {
        // Fallback: assume active
        setNodeStatus(STATUS_NODES.reduce((a, n) => ({ ...a, [n]: { status: "active" } }), {}));
      });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = useCallback(async () => {
    const raw = input.trim();
    if (!raw || loading) return;

    const userMsg = { role: "user", content: raw, mode, ts: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const newHistory = [...history, { role: "user", content: raw }];

    let res;
    try {
      res = await fetch("/api/developer/agent-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newHistory,
          mode: mode,
        }),
      });

      if (!res.ok) {
        const rawText = await res.text();
        throw new Error(`Server returned ${res.status}: ${rawText}`);
      }

      const data = await res.json();

      if (data.status === "ok") {
        const reply = data.response || "Sin respuesta.";
        if (data.provider) setLastProvider(data.provider);

        const assistantMsg = { role: "assistant", content: reply, ts: Date.now(), patches: data.patches };
        setMessages(prev => [...prev, assistantMsg]);
        setHistory([...newHistory, { role: "assistant", content: reply }]);
      } else {
        const errMsg = data.error || data.message || data.response || "Error desconocido";
        const stack = data.trace || data.stack || "No disponible";
        
        reportToAudit(new Error(errMsg), { module: "Developer", action: "agent-chat", mode: mode, data: data });
        
        setMessages(prev => [...prev, {
          role: "assistant",
          content: `❌ Error: ${errMsg}\n\nStack:\n${stack}`,
          ts: Date.now()
        }]);
      }

    } catch (e) {
      reportToAudit(e, { module: "Developer", action: "agent-chat", mode: mode });
      
      let detail = e.stack || "No disponible";
      
      setMessages(prev => [...prev, {
        role: "assistant", 
        content: `❌ Error de conexión / ejecución:\n${e.message}\n\n--- DETALLE ---\n${detail}`, 
        ts: Date.now()
      }]);
    }


    setLoading(false);
  }, [input, loading, mode, history]);


  const handleKey = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      submit();
    }
  };

  const clearSession = () => {
    setMessages([]);
    setHistory([]);
    setLastProvider(null);
  };

  const modeColor = {
    chat: "#58a6ff", review: "#d2a8ff", fix: "#ff7b72",
    arch: "#79c0ff", gen: "#3fb950"
  };

  const displayNodes = STATUS_NODES.filter(n => nodeStatus[n]);

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "100%",
      background: "#010409", color: "#e6edf3",
      fontFamily: "'IBM Plex Mono', 'JetBrains Mono', monospace",
      overflow: "hidden"
    }}>

      {/* HEADER */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "12px 20px", borderBottom: "1px solid #21262d",
        background: "#0d1117"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div style={{
            width: "32px", height: "32px", borderRadius: "8px",
            background: "linear-gradient(135deg, #1f6feb, #388bfd)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "14px", fontWeight: "700", color: "#fff"
          }}>A</div>
          <div>
            <div style={{ fontSize: "13px", fontWeight: "700", letterSpacing: "0.5px", color: "#e6edf3" }}>
              ALEGR-IA <span style={{ color: "#388bfd" }}>DEV</span>
            </div>
            <div style={{ fontSize: "10px", color: "#484f58", letterSpacing: "1px" }}>
              AGENTE SENIOR · CASCADA {lastProvider ? `· ${lastProvider}` : ""}
            </div>
          </div>
        </div>

        {/* NODE STATUS */}
        <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
          {displayNodes.map(n => (
            <div key={n} style={{
              display: "flex", alignItems: "center", gap: "4px",
              fontSize: "9px", color: "#484f58", letterSpacing: "0.5px"
            }}>
              <div style={{
                width: "5px", height: "5px", borderRadius: "50%",
                background: nodeStatus[n]?.status === "active" ? "#3fb950" : "#f85149",
                boxShadow: nodeStatus[n]?.status === "active" ? "0 0 4px #3fb950" : "none"
              }} />
              {n.replace("_", " ")}
            </div>
          ))}
          <button 
            onClick={() => { throw new Error("ALEGR-IA OS: Simulación de fallo crítico en módulo Developer solicitado por el operador."); }}
            style={{
              background: "rgba(255,123,114,0.1)", border: "1px solid rgba(255,123,114,0.2)",
              color: "#ff7b72", fontSize: "9px", padding: "2px 8px", borderRadius: "4px",
              cursor: "pointer", letterSpacing: "0.5px"
            }}
          >
            SIMULAR CRASH
          </button>
          {messages.length > 0 && (
            <button onClick={clearSession} style={{
              background: "none", border: "1px solid #21262d", borderRadius: "4px",
              color: "#484f58", fontSize: "9px", padding: "2px 8px",
              cursor: "pointer", letterSpacing: "0.5px"
            }}>LIMPIAR</button>
          )}

        </div>
      </div>

      {/* MODES */}
      <div style={{
        display: "flex", gap: "0", borderBottom: "1px solid #21262d",
        background: "#0d1117"
      }}>
        {MODES.map(m => (
          <button key={m.id} onClick={() => setMode(m.id)} style={{
            background: mode === m.id ? "#161b22" : "none",
            border: "none", borderBottom: mode === m.id ? `2px solid ${modeColor[m.id]}` : "2px solid transparent",
            color: mode === m.id ? modeColor[m.id] : "#484f58",
            padding: "8px 16px", cursor: "pointer",
            fontSize: "11px", letterSpacing: "0.5px",
            display: "flex", alignItems: "center", gap: "6px",
            transition: "all 0.15s"
          }}>
            <span style={{ fontSize: "13px" }}>{m.icon}</span>
            {m.label}
          </button>
        ))}
      </div>

      {/* MESSAGES */}
      <div style={{
        flex: 1, overflowY: "auto", padding: "20px",
        display: "flex", flexDirection: "column", gap: "20px"
      }}>
        {messages.length === 0 && (
          <div style={{
            flex: 1, display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
            color: "#21262d", textAlign: "center", gap: "12px"
          }}>
            <div style={{ fontSize: "40px" }}>⬡</div>
            <div style={{ fontSize: "13px", color: "#30363d" }}>
              Agente Developer Senior activo
            </div>
            <div style={{ fontSize: "11px", color: "#21262d", maxWidth: "380px", lineHeight: 1.7 }}>
              Conectado a la cascada de proveedores de ALEGR-IA.<br />
              Seleccioná un modo y escribí tu consulta.
            </div>
            <div style={{
              display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px",
              marginTop: "16px", maxWidth: "420px"
            }}>
              {[
                "Revisá el BUG-01 de BrandService serialización",
                "Implementá el Audit Log en tiempo real para AnimaUI",
                "Cómo conectar alert_level del RuleEngine a la UI",
                "Fix completo para el módulo Noticias",
              ].map((s, i) => (
                <button key={i} onClick={() => setInput(s)} style={{
                  background: "#0d1117", border: "1px solid #21262d",
                  borderRadius: "6px", color: "#484f58", fontSize: "10px",
                  padding: "8px 10px", cursor: "pointer", textAlign: "left",
                  lineHeight: 1.5, transition: "all 0.15s",
                  fontFamily: "inherit"
                }}
                  onMouseEnter={e => { e.target.style.borderColor = "#388bfd"; e.target.style.color = "#58a6ff"; }}
                  onMouseLeave={e => { e.target.style.borderColor = "#21262d"; e.target.style.color = "#484f58"; }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex", flexDirection: "column",
            alignItems: msg.role === "user" ? "flex-end" : "flex-start",
            gap: "4px"
          }}>
            {msg.role === "user" ? (
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{
                  fontSize: "9px", color: modeColor[msg.mode] || "#484f58",
                  border: `1px solid ${modeColor[msg.mode] || "#21262d"}`,
                  padding: "1px 5px", borderRadius: "3px", letterSpacing: "0.5px"
                }}>
                  {MODES.find(m => m.id === msg.mode)?.label || "CHAT"}
                </span>
                <div style={{
                  background: "#1c2128", border: "1px solid #30363d",
                  borderRadius: "8px 8px 2px 8px",
                  padding: "10px 14px", maxWidth: "75%",
                  fontSize: "13px", lineHeight: 1.6, color: "#cdd9e5"
                }}>
                  {msg.content}
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", gap: "10px", maxWidth: "92%", alignItems: "flex-start" }}>
                <div style={{
                  width: "22px", height: "22px", borderRadius: "6px",
                  background: "linear-gradient(135deg, #1f6feb, #388bfd)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "10px", fontWeight: "700", color: "#fff",
                  flexShrink: 0, marginTop: "2px"
                }}>A</div>
                <div style={{
                  background: "#0d1117", border: "1px solid #21262d",
                  borderRadius: "2px 8px 8px 8px",
                  padding: "12px 16px",
                  fontSize: "13px", lineHeight: 1.7, color: "#cdd9e5",
                  flex: 1
                }}>
                  {renderContent(msg.content)}
                  {msg.patches && msg.patches.length > 0 && (
                    <div style={{ backgroundColor: "#000", border: "1px solid #3fb950", padding: "12px", marginTop: "8px", borderRadius: "4px" }}>
                      <h4 style={{ color: "#3fb950", margin: "0 0 8px 0" }}>🧩 Patches detectados</h4>
                      {msg.patches.map((p, j) => (
                        <div key={j} style={{ marginTop: "8px" }}>
                          <div style={{ fontSize: "11px", color: "#8b949e", marginBottom: "4px" }}>{p.file}</div>
                          <pre style={{ fontSize: "11px", background: "#0d1117", color: "#3fb950", padding: "12px", overflow: "auto", border: "1px solid #3fb950", borderRadius: "4px" }}>
                            {p.diff_preview || p.diff || p.raw}
                          </pre>
                          <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                            <button
                              onClick={() => navigator.clipboard.writeText(p.diff || p.content || p.raw)}
                              style={{ fontSize: "11px", background: "#1f6feb", color: "#fff", border: "none", padding: "4px 8px", cursor: "pointer", borderRadius: "3px" }}
                            >
                              Copiar Patch
                            </button>
                            <button
                              onClick={async () => {
                                try {
                                  const res = await fetch("/api/developer/dry-run", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                      file: p.file,
                                      content: p.content || p.diff || p.raw
                                    })
                                  });
                                  const json = await res.json();
                                  if (json.status === "success") {
                                    alert(`✅ Validación exitosa en Sandbox!\n${json.message}`);
                                  } else {
                                    alert(`❌ Error en Sandbox (${json.stage}):\n${json.error}`);
                                  }
                                } catch (e) {
                                  alert(`❌ Fallo red: ${e.message}`);
                                }
                              }}
                              style={{ fontSize: "11px", background: "#f85149", color: "#fff", border: "none", padding: "4px 8px", cursor: "pointer", borderRadius: "3px" }}
                            >
                              Dry Run (Sandbox)
                            </button>
                            <button
                              onClick={async () => {
                                try {
                                  const res = await fetch("/api/developer/sandbox-test", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                      file: p.file,
                                      content: p.content || p.diff || p.raw
                                    })
                                  });
                                  const json = await res.json();
                                  
                                  // Actualizamos el estado del mensaje para mostrar resultados
                                  setMessages(prev => prev.map((m, idx) => {
                                    if (idx === i) {
                                      const newPatches = [...m.patches];
                                      newPatches[j] = { 
                                        ...p, 
                                        testResults: json.tests, 
                                        semanticResults: json.semantic,
                                        confidence: json.confidence,
                                        sandboxStatus: json.status 
                                      };
                                      return { ...m, patches: newPatches };
                                    }
                                    return m;
                                  }));

                                  if (json.status === "ok") {
                                    // No alert, el UI se actualiza
                                  } else {
                                    alert(`❌ Fallo en Sandbox:\n${json.message || json.error}`);
                                  }
                                } catch (e) {
                                  alert(`❌ Fallo red: ${e.message}`);
                                }
                              }}
                              style={{ fontSize: "11px", background: "#d29922", color: "#fff", border: "none", padding: "4px 8px", cursor: "pointer", borderRadius: "3px" }}
                            >
                              Sandbox Test (Boot + Assertions)
                            </button>
                            <button
                              onClick={async () => {
                                try {
                                  const res = await fetch("/api/developer/apply-patch", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                      file: p.file,
                                      content: p.content || p.diff || p.raw
                                    })
                                  });
                                  const json = await res.json();
                                  if (json.status === "applied") {
                                    alert(`✅ Aplicado correctamente! Backup en:\n${json.backup}`);
                                  } else {
                                    alert(`❌ Error aplicando:\n${json.error}`);
                                  }
                                } catch (e) {
                                  alert(`❌ Fallo red: ${e.message}`);
                                }
                              }}
                              style={{ fontSize: "11px", background: "#3fb950", color: "#fff", border: "none", padding: "4px 8px", cursor: "pointer", borderRadius: "3px" }}
                            >
                              Apply Patch
                            </button>
                          </div>
                          <SandboxTestResults 
                            results={p.testResults} 
                            semantic={p.semanticResults} 
                            confidence={p.confidence}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            <span style={{
              fontSize: "9px", color: "#21262d",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              paddingLeft: msg.role === "assistant" ? "32px" : "0"
            }}>
              {new Date(msg.ts).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })}
            </span>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
            <div style={{
              width: "22px", height: "22px", borderRadius: "6px",
              background: "linear-gradient(135deg, #1f6feb, #388bfd)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "10px", color: "#fff", flexShrink: 0, marginTop: "2px"
            }}>A</div>
            <div style={{
              background: "#0d1117", border: "1px solid #21262d",
              borderRadius: "2px 8px 8px 8px", padding: "12px 16px",
              display: "flex", gap: "4px", alignItems: "center"
            }}>
              {[0, 0.2, 0.4].map((d, i) => (
                <div key={i} style={{
                  width: "5px", height: "5px", borderRadius: "50%",
                  background: "#388bfd",
                  animation: "devagent-pulse 1.2s ease-in-out infinite",
                  animationDelay: `${d}s`
                }} />
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div style={{
        padding: "14px 20px", borderTop: "1px solid #21262d",
        background: "#0d1117"
      }}>
        <div style={{
          display: "flex", gap: "10px", alignItems: "flex-end"
        }}>
          <div style={{
            flex: 1, background: "#161b22", border: "1px solid #30363d",
            borderRadius: "8px", padding: "10px 14px",
            display: "flex", flexDirection: "column", gap: "6px",
            transition: "border-color 0.15s"
          }}>
            {mode !== "chat" && (
              <div style={{
                fontSize: "9px", color: modeColor[mode],
                letterSpacing: "0.5px", display: "flex", alignItems: "center", gap: "4px"
              }}>
                <span>{MODES.find(m => m.id === mode)?.icon}</span>
                MODO {MODES.find(m => m.id === mode)?.label.toUpperCase()}
              </div>
            )}
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder={
                mode === "review" ? "Pegá el código a revisar..." :
                mode === "fix" ? "Describí el bug o pegá el stack trace..." :
                mode === "arch" ? "Describí la decisión arquitectónica..." :
                mode === "gen" ? "Describí qué necesitás generar..." :
                "Consultá sobre ALEGR-IA..."
              }
              rows={3}
              style={{
                background: "none", border: "none", outline: "none",
                color: "#e6edf3", fontSize: "13px", lineHeight: 1.6,
                resize: "none", fontFamily: "inherit",
                width: "100%", boxSizing: "border-box"
              }}
            />
          </div>
          <button
            onClick={submit}
            disabled={!input.trim() || loading}
            style={{
              background: input.trim() && !loading
                ? "linear-gradient(135deg, #1f6feb, #388bfd)"
                : "#161b22",
              border: "1px solid #30363d", borderRadius: "8px",
              color: input.trim() && !loading ? "#fff" : "#484f58",
              padding: "12px 18px", cursor: input.trim() && !loading ? "pointer" : "not-allowed",
              fontSize: "13px", fontFamily: "inherit",
              transition: "all 0.15s", flexShrink: 0, alignSelf: "flex-end",
              minWidth: "80px"
            }}
          >
            {loading ? "..." : "⏎ cmd"}
          </button>
        </div>
        <div style={{
          fontSize: "9px", color: "#21262d", marginTop: "6px",
          display: "flex", justifyContent: "space-between"
        }}>
          <span>Ctrl+Enter para enviar</span>
          <span>{Math.floor(history.length / 2)} turnos · {messages.length} msgs{lastProvider ? ` · ${lastProvider}` : ""}</span>
        </div>
      </div>

      <style>{`
        @keyframes devagent-pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
}
