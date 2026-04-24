import React, { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("🔥 ERROR CAPTURADO:", error, errorInfo);
    this.setState({ error, errorInfo });
    
    // Opcional: Emitir a AuditEmitter (Backend)
    this.reportToAudit(error, errorInfo);
  }

  async reportToAudit(error: Error, errorInfo: ErrorInfo) {
    try {
      await fetch("/api/anima/audit/error", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          timestamp: new Date().toISOString(),
          context: {
            url: window.location.href,
            userAgent: navigator.userAgent
          }
        })
      });
    } catch (e) {
      console.warn("⚠️ No se pudo reportar el error al AuditEmitter:", e);
    }
  }

  formatError() {
    const { error, errorInfo } = this.state;

    return `
=== ALEGR-IA ERROR REPORT ===

Message:
${error?.message}

Stack:
${error?.stack}

Component Stack:
${errorInfo?.componentStack}

Timestamp:
${new Date().toISOString()}

Environment:
URL: ${window.location.href}
UA: ${navigator.userAgent}
`;
  }

  copyToClipboard = () => {
    navigator.clipboard.writeText(this.formatError());
    // Usamos una notificación nativa o simple para evitar dependencias extras
    alert("Error copiado ✅");
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
          <div className="bg-[#1a0b0b] border border-red-500/30 text-white p-8 rounded-3xl max-w-2xl w-full shadow-2xl">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center text-red-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-black uppercase tracking-tighter text-red-400">
                  ⚠️ Error Crítico de Coherencia
                </h2>
                <p className="text-zinc-500 text-xs font-mono tracking-widest uppercase">
                  Sovereign Kernel Interruption
                </p>
              </div>
            </div>

            <p className="mb-6 text-zinc-300 text-sm leading-relaxed">
              Un módulo del sistema operativo ha colapsado. Se ha generado un reporte técnico para auditoría.
              Podés copiarlo para debug o intentar recargar el nexo.
            </p>

            <div className="relative group mb-6">
              <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-purple-500/20 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
              <textarea
                readOnly
                value={this.formatError()}
                className="relative w-full h-48 bg-black/60 border border-white/5 text-red-200/70 p-4 text-[10px] font-mono rounded-xl custom-scrollbar outline-none focus:border-red-500/30 transition-all"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={this.copyToClipboard}
                className="flex-1 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 font-bold py-3 rounded-xl transition-all active:scale-95 uppercase text-[11px] tracking-widest"
              >
                Copiar Reporte
              </button>

              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold py-3 rounded-xl transition-all active:scale-95 uppercase text-[11px] tracking-widest"
              >
                Reiniciar Nexus
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
