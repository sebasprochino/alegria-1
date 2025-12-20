import { useEffect, useState } from "react";
import AnimaUI from "./anima/AnimaUI";

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [animaAwake, setAnimaAwake] = useState(false);

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  // 🔌 Estado del sistema
  useEffect(() => {
    fetch("http://localhost:8000/system/status")
      .then(res => res.json())
      .then(data => setSystemStatus(data))
      .catch(() => setSystemStatus({ status: "offline" }));
  }, []);

  // 🌱 Despertar de Anima
  useEffect(() => {
    if (systemStatus?.status === "ok") {
      setAnimaAwake(true);
    }
  }, [systemStatus]);

  // 💬 Envío de mensajes
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });

      const data = await res.json();

      // 🧠 Autonomía básica de Anima
      if (Math.random() > 0.35) {
        setMessages(prev => [
          ...prev,
          {
            role: "anima",
            content: data.reply || "Anima guarda silencio."
          }
        ]);
      }
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: "anima",
          content: "Anima: el canal aún se está formando."
        }
      ]);
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: "monospace" }}>
      <h2>🌳 ALEGR-IA OS</h2>

      <p>
        Estado del sistema:{" "}
        <strong>{systemStatus?.status || "verificando…"}</strong>
      </p>

      {/* Gateway de chat */}
      <div style={{ marginTop: 20 }}>
        <div
          style={{
            border: "1px solid #444",
            padding: 10,
            height: 300,
            overflowY: "auto",
            marginBottom: 10
          }}
        >
          {messages.map((m, i) => (
            <div key={i} style={{ marginBottom: 6 }}>
              <strong>{m.role === "user" ? "Vos" : "Anima"}:</strong>{" "}
              {m.content}
            </div>
          ))}
        </div>

        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Decile algo a Anima…"
          style={{ width: "80%", marginRight: 6 }}
        />

        <button onClick={sendMessage}>Enviar</button>
      </div>

      {/* 🧠 Presencia consciente */}
      {animaAwake && <AnimaUI messages={messages} />}
    </div>
  );
}

export default App;
