/**
 * messageAdapter.ts — Capa de normalización ALEGR-IA OS
 *
 * Backend piensa → Adapter ordena → UI muestra.
 *
 * REGLAS DEL ADAPTER:
 *   ✔ Solo mapea estructura → estructura
 *   ✔ Provee fallbacks seguros (nunca undefined en campos críticos)
 *   ✘ NO interpreta semántica
 *   ✘ NO toma decisiones
 *   ✘ NO llama al backend
 */

// 1. Tipos Básicos Redefinidos (Evitamos ambigüedad legado)
export type MessageType = "llm" | "tool" | "strategy" | "system" | "error";

export interface SmokeSpan {
  start: number;
  end: number;
  type: "emotional" | "authority" | "meta" | string;
  pattern: string;
  reason: string;
}

export interface Analysis {
  confidence: number;
  flags: string[];
  smoke_spans: SmokeSpan[];
  smoke_signals: string[];
  type: string[] | string;
  parse_mode?: string;
  fluff_detected?: boolean;
  alert_level?: "none" | "warning" | "critical";
}

export interface Option {
  id: string;
  label: string;
  description?: string;
  risk?: string;
}

export interface UIMessage {
  type: MessageType;
  content: any;
  meta?: {
    source?: string;
    timestamp?: number;
    raw?: string;
    analysis?: Analysis;
    confidenceLevel?: string;
    hasSmoke?: boolean;
    autoExecute?: boolean;
    alertLevel?: string;
    trace?: any;
    intentionId?: string;
    mode?: string;
    navPayload?: any;
    [key: string]: any;
  };
}

const EMPTY_ANALYSIS: Analysis = {
  confidence: 1.0,
  flags: [],
  smoke_spans: [],
  smoke_signals: [],
  type: ["informational"],
  parse_mode: "raw",
  fluff_detected: false,
  alert_level: "none",
};

const AUTHORIZED_STATUSES = new Set(["authorized", "Authorized", "ok", "OK", "completed", "Completed"]);
const DECISION_STATUSES = new Set(["doubt", "Doubt"]);
const ERROR_STATUSES = new Set(["error", "Error", "rejected", "Rejected"]);

function deriveConfidenceLevel(confidence: number): "high" | "medium" | "low" {
  if (confidence >= 0.8) return "high";
  if (confidence >= 0.5) return "medium";
  return "low";
}

function normalizeAnalysis(raw: unknown): Analysis {
  if (!raw || typeof raw !== "object") return EMPTY_ANALYSIS;
  const a = raw as Record<string, unknown>;
  return {
    confidence:    typeof a.confidence === "number" ? a.confidence : 1.0,
    flags:         Array.isArray(a.flags)           ? (a.flags as string[]) : [],
    smoke_spans:   Array.isArray(a.smoke_spans)     ? (a.smoke_spans as SmokeSpan[]) : [],
    smoke_signals: Array.isArray(a.smoke_signals)   ? (a.smoke_signals as string[]) : [],
    type:          (typeof a.type === "string" || Array.isArray(a.type)) ? (a.type as string | string[]) : ["informational"],
    parse_mode:    typeof a.parse_mode === "string" ? a.parse_mode : undefined,
    fluff_detected: Boolean(a.fluff_detected),
    alert_level:   (a.alert_level as "none" | "warning" | "critical") || "none",
  };
}

function normalizeOptions(raw: unknown): Option[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((o: unknown) => {
    const opt = o as Record<string, unknown>;
    return {
      id:          String(opt.id ?? ""),
      label:       String(opt.label ?? opt.id ?? opt.strategy ?? "Opción"),
      description: typeof opt.description === "string" ? opt.description : undefined,
      risk:        typeof opt.risk        === "string" ? opt.risk        : undefined,
    };
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Adapter principal
// ─────────────────────────────────────────────────────────────────────────────

export function adaptBackendResponse(data: any): UIMessage {
  const status: string = String(data?.status ?? "").toLowerCase();
  const intentionId = data?.intention_id;
  const mode: string = data?.mode ?? "intention";

  const raw = String(data?.meta?.raw ?? data?.raw_attempt ?? data?.rawAttempt ?? "");
  const analysis = normalizeAnalysis(data?.meta?.analysis ?? data?.analysis);
  const msgText = String(data.message ?? data.response ?? "");
  
  const baseMeta = {
    raw,
    analysis,
    confidenceLevel: deriveConfidenceLevel(analysis.confidence),
    hasSmoke: analysis.fluff_detected,
    autoExecute: Boolean(data.auto),
    alertLevel: analysis.alert_level,
    trace: data.trace,
    source: data.source || data.meta?.source,
    mode,
    intentionId,
    insight: data.insight
  };

  // ── 0. DECISION (STRATEGY) ─────────────────────────────────────────────────
  if (DECISION_STATUSES.has(data?.status) || data?.paths) {
    return {
      type: "strategy",
      content: normalizeOptions(data.options || data.paths),
      meta: baseMeta
    };
  }

  // ── 1. ERROR ───────────────────────────────────────────────────────────────
  if (ERROR_STATUSES.has(data?.status) || status === "rejected") {
    return {
      type: "error",
      content: data.message ?? data.response ?? data.reason ?? "Error del sistema.",
      meta: baseMeta
    };
  }

  // --- HUMANIZAR CONTENIDO TÉCNICO (Anti-JSON en el chat) ---
  let cleanMsgText = msgText.trim();
  // Limpiar formateo de bloques de código Markdown (```json ... ```) si existe
  if (cleanMsgText.startsWith("```")) {
     cleanMsgText = cleanMsgText.replace(/^```[a-z]*\s*/i, "").replace(/\s*```$/i, "").trim();
  }

  if (cleanMsgText.startsWith("{") && cleanMsgText.endsWith("}")) {
    let parsed: any = null;
    
    // Intento 1: Parseo JSON estándar
    try {
      parsed = JSON.parse(cleanMsgText);
    } catch (e) {
      // Intento 2: Backend devolvió un string de diccionario Python con comillas simples
      try {
        const sanitized = cleanMsgText.replace(/'/g, '"');
        parsed = JSON.parse(sanitized);
      } catch (e2) {
        // Intento 3: Extracción por Regex
        if (msgText.includes("action") || msgText.includes("status")) {
           parsed = { action: "fallback" };
           const cmdMatch = msgText.match(/['"]commands['"]\s*:\s*\[\s*['"]([^\]]+)['"]\s*\]/);
           if (cmdMatch) parsed.commands = [cmdMatch[1].replace(/['"]/g, '')];
           const statusMatch = msgText.match(/['"]status['"]\s*:\s*['"]([^'"]+)['"]/);
           if (statusMatch) parsed.status = statusMatch[1];
        }
      }
    }

    if (parsed) {
      // Si el objeto tiene trazas de ser una estructura del sistema (action o status)
      if (parsed.action || parsed.status) {
        let finalContent = "";
        
        // Priority 1: Comandos (Lista de mensajes del OS)
        if (Array.isArray(parsed.commands) && parsed.commands.length > 0) {
          finalContent = parsed.commands.map((c: string) => {
             if (c === "No saludos genéricos") return "🔴 Omitido por protocolo: No saludos genéricos";
             return c;
          }).join(". ");
        } 
        
        // Priority 2: Status (A veces el backend mete el mensaje humano aquí cuando no hay comandos)
        if (!finalContent && typeof parsed.status === 'string' && parsed.status.length > 5) {
           if (parsed.status === "Rechazado" || parsed.status === "Rejected") {
             finalContent = "🔴 Acción omitida por política del sistema.";
           } else {
             finalContent = parsed.status;
           }
        }

        // Priority 3: Otros campos estándar
        if (!finalContent) {
          finalContent = parsed.reason || parsed.message || parsed.response || parsed.error;
        }

        // SIEMPRE que detectemos una acción técnica del OS (task_execute, navigate, etc.)
        // forzamos el tipo a LLM para evitar el renderizado de bloque técnico (emerald/green).
        // Si no encontramos texto humano, usamos un fallback amigable.
        return {
          type: "llm",
          content: finalContent || "Procesando operación del sistema...",
          meta: baseMeta
        };
      }
    }
  }

  // ── 2. LLM (CONVERSACIÓN PURA) ─────────────────────────────────────────────
  if (mode === "conversation" || (mode === "intention" && !data.source)) {
    return {
      type: "llm",
      content: msgText,
      meta: baseMeta
    };
  }

  // ── 3. TOOL OUTPUT (REALIDAD TÉCNICA O EJECUCIÓN) ──────────────────────────
  if (AUTHORIZED_STATUSES.has(data?.status) || mode === "execution") {
    let navPayload: any = undefined;
    
    // Extracción de Navegación (System)
    if (msgText.startsWith("{") && msgText.endsWith("}")) {
        try {
            const parsed = JSON.parse(msgText);
            if (parsed.action === "navigate" && parsed.url) {
                navPayload = {
                    url: parsed.url,
                    name: parsed.name ?? "Web",
                    action: parsed.action
                };
            }
        } catch (e) { }
    }

    // Parseo inteligente de contenido si es JSON real (radar o datos estructurados)
    let parsedContent: any = msgText;
    try {
       const o = JSON.parse(msgText);
       if(typeof o === "object") parsedContent = o;
    } catch(e) {}

    return {
      type: "tool",
      content: parsedContent,
      meta: {
        ...baseMeta,
        navPayload
      }
    };
  }

  // ── 4. FALLBACK ────────────────────────────────────────────────────────────
  console.warn("[MessageAdapter] Status no reconocido:", data?.status, data);
  return {
    type: "system",
    content: data?.message ?? data?.response ?? "Respuesta generica",
    meta: baseMeta
  };
}

export async function adaptNetworkError(error: any, response?: Response): Promise<UIMessage> {
  const message = error?.message || "Sin mensaje";
  const stack = error?.stack || "No disponible";
  let rawText = "";

  if (response) {
    try {
      rawText = await response.text();
    } catch (e) {
      rawText = "No se pudo leer la respuesta";
    }
  }

  return {
    type: "error",
    content: `❌ Error de Conexión / Kernel:
${message}

${rawText ? `--- RAW RESPONSE ---
${rawText}` : ""}

Stack Trace:
${stack}`,
    meta: {
      alertLevel: "critical",
      timestamp: Date.now()
    }
  };
}

