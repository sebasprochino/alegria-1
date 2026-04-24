import { useRef, useState } from "react";

interface Props {
  messages: any[];
  onVoiceInput: (text: string) => void;
}

export default function AnimaVoice({ onVoiceInput }: Props) {
  const recognitionRef = useRef<any>(null);
  const [enabled, setEnabled] = useState(false);

  const startListening = () => {
    if (enabled) return;

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = "es-AR";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      onVoiceInput(text);
    };

    recognition.onerror = () => {
      recognition.stop();
      setEnabled(false);
    };

    recognition.onend = () => {
      setEnabled(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setEnabled(true);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setEnabled(false);
  };

  return (
    <div className="p-2">
      <button
        onClick={enabled ? stopListening : startListening}
        className={`px-3 py-2 rounded-full border-none cursor-pointer text-white transition-colors ${
          enabled ? "bg-[#25d366]" : "bg-[#2a3942]"
        }`}
      >
        {enabled ? "Escuchando…" : "Activar voz"}
      </button>
    </div>
  );
}
