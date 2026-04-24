/**
 * Enriquecedor de errores para ALEGR-IA OS.
 * Añade contexto operativo a los fallos de la UI para facilitar el debugging.
 */
export function enrichError(error, context = {}) {
  const enriched = {
    message: error?.message || "Unknown error",
    stack: error?.stack,
    context: {
      ...context,
      url: window.location.href,
      timestamp: new Date().toISOString()
    }
  };
  
  // Loguear para visibilidad inmediata en consola
  console.group("🧠 ALEGR-IA ENRICHED ERROR");
  console.error("Message:", enriched.message);
  console.log("Context:", enriched.context);
  console.groupEnd();
  
  return enriched;
}

/**
 * Reporta un error al AuditEmitter sin necesidad de crashear la UI.
 */
export async function reportToAudit(error, context = {}) {
  const enriched = enrichError(error, context);
  try {
    await fetch("/api/anima/audit/error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: enriched.message,
        stack: enriched.stack,
        context: enriched.context,
        timestamp: enriched.context.timestamp
      })
    });
  } catch (e) {
    console.warn("⚠️ No se pudo reportar al AuditEmitter:", e);
  }
}

