import React from 'react';

export default function LexiconPanel({ messages }) {
  if (!messages) return null;
  
  const last = messages.slice(-6);

  const detectDrift = (current, previous) => {
    if (!previous) return false;
    // Si la intención cambia, hay deriva
    return current.intent !== previous.intent;
  };

  return (
    <div className="w-72 h-full border-l border-white/5 p-4 text-xs space-y-4 bg-[#0b141a] overflow-y-auto custom-scrollbar flex-shrink-0 hidden lg:block shadow-2xl z-20">
      
      <div className="flex items-center gap-2 mb-2">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        <div className="text-zinc-500 font-bold uppercase tracking-[0.2em] text-[10px]">LEXICON OBSERVER</div>
      </div>

      {last.map((m, i) => {
        // En nuestro messageAdapter actual los metadatos podrían estar en analysis (o meta temporalmente)
        const l = m.meta?.lexicon || m.analysis?.lexicon;
        if (!l) return null;

        const prevM = i > 0 ? last[i - 1] : null;
        const prevLexicon = prevM ? (prevM.meta?.lexicon || prevM.analysis?.lexicon) : null;

        return (
          <div key={i} className="bg-zinc-950/50 border border-zinc-800/50 p-3 rounded-lg relative overflow-hidden transition-all hover:bg-zinc-900/50 hover:border-zinc-700/50 group">
            
            {detectDrift(l, prevLexicon) && (
              <div className="absolute top-2 right-2 px-1.5 py-[2px] bg-red-500/10 text-red-400 font-bold tracking-widest uppercase rounded text-[7px] border border-red-500/20 shadow-glow-sm">
                Deriva
              </div>
            )}

            <div className="text-zinc-500 uppercase tracking-widest text-[9px] mb-2 flex items-center gap-1">
              INTENT: <span className="text-zinc-300 font-mono lowercase bg-black/40 px-1 py-0.5 rounded">{l.intent}</span>
            </div>

            <div className="mb-2">
              <div className="text-[8px] text-zinc-600 uppercase tracking-widest mb-1">ENTITIES</div>
              <div className="flex flex-wrap gap-1">
                {l.entities?.map(e => (
                  <span key={e} className="px-1.5 py-0.5 bg-blue-500/10 border border-blue-500/20 rounded text-blue-400 text-[10px] whitespace-nowrap">
                    {e}
                  </span>
                ))}
                {!l.entities?.length && <span className="text-zinc-700 text-[10px] italic">none</span>}
              </div>
            </div>

            <div className="mt-2 text-zinc-400 italic text-[11px] leading-relaxed border-t border-zinc-800/50 pt-2">
               &ldquo;{l.pattern}&rdquo;
            </div>

          </div>
        );
      })}

      {/* Si no hay mensajes con data en lexicon aún */}
      {last.filter(m => m.meta?.lexicon || m.analysis?.lexicon).length === 0 && (
         <div className="h-full flex flex-col items-center justify-center text-zinc-700 opacity-50 space-y-2 mt-12">
            <div className="w-8 h-8 rounded-lg border border-zinc-700 border-dashed flex items-center justify-center mb-2">
               <span className="text-zinc-500 text-lg">👁</span>
            </div>
            <p className="font-mono text-[9px] uppercase tracking-widest text-center">Esperando<br/>Tráfico Cognitivo...</p>
         </div>
      )}
    </div>
  );
}
