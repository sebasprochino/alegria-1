from pathlib import Path
from datetime import datetime

BASE = Path(r"G:\ALEGRIA_OS\ALEGRIA_OS")
APP = BASE / "frontend" / "src" / "App.jsx"
BACKUP = BASE / "_backup_chat"

CHAT_APP = """import { useState, useEffect, useRef } from "react";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const lastSpoken = useRef(null);

  const speak = (text) => {
    if (!("speechSynthesis" in window)) return;
    if (text === lastSpoken.current) return;
    lastSpoken.current = text;

    const u = new SpeechSynthesisUtterance(text);
    u.lang = "es-AR";
    u.rate = 0.95;
    u.pitch = 1.05;
    window.speechSynthesis.speak(u);
  };

  const send = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content }),
      });

      const data = await res.json();
      const reply = data.reply || "Estoy acá.";

      const animaMsg = { role: "anima", content: reply };
      setMessages((m) => [...m, animaMsg]);
      speak(reply);
    } catch {
      const fail = "El canal todavía se está formando.";
      setMessages((m) => [...m, { role: "anima", content: fail }]);
      speak(fail);
    }
  };

  return (
    <div style={{
      fontFamily: "monospace",
      padding: 20,
      background: "#0e0e0e",
      color: "#e6e6e6",
      height: "100vh"
    }}>
      <h2>🧠 Anima Chordata</h2>

      <div style={{
        border: "1px solid #333",
        padding: 10,
        height: "70vh",
        overflowY: "auto",
        marginBottom: 10
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <strong>{m.role === "user" ? "Vos" : "Anima"}:</strong> {m.content}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && send()}
        placeholder="Hablá con Anima…"
        style={{ width: "80%", marginRight: 6 }}
      />
      <button onClick={send}>Enviar</button>
    </div>
  );
}

export default App;
"""

def main():
    if not APP.exists():
        print("❌ App.jsx no encontrado")
        return

    BACKUP.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP / f"App_chat_{ts}.jsx"
    backup.write_text(APP.read_text(encoding="utf-8"), encoding="utf-8")

    APP.write_text(CHAT_APP, encoding="utf-8")
    print("✔ Chat con Anima Chordata activado")
    print("🔁 Reiniciá Vite")

if __name__ == "__main__":
    main()
