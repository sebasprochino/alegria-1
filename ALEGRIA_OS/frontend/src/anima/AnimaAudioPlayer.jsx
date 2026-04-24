import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square } from 'lucide-react';

export default function AnimaAudioPlayer({ text, isUser }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const intervalRef = useRef(null);

    const stop = () => {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        setProgress(0);
        if (intervalRef.current) clearInterval(intervalRef.current);
    };

    const play = () => {
        const selection = window.getSelection().toString();
        const textToRead = selection || text;

        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(textToRead);
        u.lang = "es-AR";

        u.onstart = () => {
            setIsPlaying(true);
            let p = 0;
            // Estimación de duración para la barra de progreso
            const estimatedDuration = Math.max(1000, textToRead.length * 60);
            const intervalTime = 100;
            const step = (intervalTime / estimatedDuration) * 100;

            intervalRef.current = setInterval(() => {
                p += step;
                if (p >= 100) p = 100;
                setProgress(p);
            }, intervalTime);
        };

        u.onend = stop;
        u.onerror = stop;

        window.speechSynthesis.speak(u);
    };

    useEffect(() => () => stop(), []);

    return (
        <div className="flex items-center gap-2 mt-2 pt-1 border-t border-white/5 select-none">
            <button
                onClick={isPlaying ? stop : play}
                className={`p-1.5 rounded-full flex items-center justify-center transition-colors ${isUser
                    ? 'bg-black/20 hover:bg-black/30 text-[#e9edef]'
                    : 'bg-[#00a884] hover:bg-[#008f6f] text-white'
                    }`}
            >
                {isPlaying ? <Square size={12} fill="currentColor" /> : <Play size={12} fill="currentColor" />}
            </button>
            <div className="flex-1 h-1 bg-black/10 rounded-full overflow-hidden">
                <div
                    className={`h-full transition-all duration-100 ${isUser ? 'bg-white/50' : 'bg-[#00a884]'}`}
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    );
}