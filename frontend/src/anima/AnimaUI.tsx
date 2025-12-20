import { useEffect, useRef } from "react";

export default function AnimaUI({ messages }) {
  const lastSpoken = useRef(null);

  useEffect(() => {
    if (!messages || messages.length === 0) return;

    const last = messages[messages.length - 1];

    if (last.role !== "anima") return;
    if (last.content === lastSpoken.current) return;

    lastSpoken.current = last.content;

    if ("speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(last.content);
      u.lang = "es-AR";
      u.rate = 0.95;
      u.pitch = 1.05;
      window.speechSynthesis.speak(u);
    }
  }, [messages]);

  return (
    <div style={{
      position: "fixed",
      bottom: 12,
      right: 12,
      opacity: 0.6,
      fontSize: 12
    }}>
      🧠 Anima presente
    </div>
  );
}
