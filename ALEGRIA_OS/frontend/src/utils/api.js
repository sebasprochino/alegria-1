import { resolveIntent } from './router.js';

const AGENT_ROUTES = {
  'nexus:': '/nexus/update',
  'radar:': '/radar/query',
  'dev:':   '/developer/execute'
};

export async function sendMessage(input, state, history) {
  let endpoint = "/anima/chat";
  
  // Transformación de intención (Triggers)
  const finalInput = resolveIntent(input);

  // Routing (Destino)
  const prefix = Object.keys(AGENT_ROUTES).find(p => finalInput.startsWith(p));
  if (prefix) endpoint = AGENT_ROUTES[prefix];

  const response = await fetch(`/api${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      input: finalInput,
      state,
      history: history.slice(-6)
    }),
  });

  return await response.json();
}
