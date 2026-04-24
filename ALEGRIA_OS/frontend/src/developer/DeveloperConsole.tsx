import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, Terminal, Activity, Database, Shield, Zap, Search, Wifi, WifiOff, Trash2, Pause, Play } from 'lucide-react';

interface Props {
  onBack: () => void;
}

// ─── Types ────────────────────────────────────────────────────────────────────

type Stage = 'received' | 'provider' | 'guard' | 'antigravity' | 'response' | 'error' | 'override';
type FilterLevel = 'ALL' | 'ERROR' | 'WARN' | 'INFO';

interface AuditEvent {
  id: string; // local uuid para key React
  intention_id: string;
  stage: Stage;
  timestamp: number;
  agent: string;
  data: Record<string, any>;
  receivedAt: number; // ms local para ordenar
}

type Tab = 'console' | 'logs' | 'architecture';

// ─── Constants ────────────────────────────────────────────────────────────────

const SSE_URL = '/api/anima/audit/stream';
const MAX_EVENTS = 200; // buffer máximo — más viejo se descarta

const STAGE_META: Record<Stage, { label: string; color: string; bg: string; symbol: string }> = {
  received:    { label: 'RECEIVED',    color: '#58a6ff', bg: 'rgba(88,166,255,0.08)',   symbol: '→' },
  provider:    { label: 'PROVIDER',    color: '#d2a8ff', bg: 'rgba(210,168,255,0.08)',  symbol: '⬡' },
  guard:       { label: 'GUARD',       color: '#f2cc60', bg: 'rgba(242,204,96,0.08)',   symbol: '⚑' },
  antigravity: { label: 'ANTIGRAVITY', color: '#79c0ff', bg: 'rgba(121,192,255,0.08)',  symbol: '⊕' },
  response:    { label: 'RESPONSE',    color: '#3fb950', bg: 'rgba(63,185,80,0.08)',    symbol: '✓' },
  error:       { label: 'ERROR',       color: '#ff7b72', bg: 'rgba(255,123,114,0.12)',  symbol: '✘' },
  override:    { label: 'OVERRIDE',    color: '#ffa657', bg: 'rgba(255,166,87,0.08)',   symbol: '!' },
};

function stageMeta(stage: string) {
  return STAGE_META[stage as Stage] ?? { label: stage.toUpperCase(), color: '#8b949e', bg: 'rgba(139,148,158,0.08)', symbol: '·' };
}

function stageToFilterLevel(stage: Stage): FilterLevel {
  if (stage === 'error') return 'ERROR';
  if (stage === 'guard' || stage === 'override' || stage === 'antigravity') return 'WARN';
  return 'INFO';
}

function formatTs(ts: number): string {
  return new Date(ts).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatData(data: Record<string, any>): string {
  try {
    return JSON.stringify(data, null, 0)
      .replace(/"/g, '')
      .replace(/,/g, ' · ')
      .replace(/[{}]/g, '')
      .slice(0, 120);
  } catch {
    return String(data);
  }
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StreamBadge({ connected, paused }: { connected: boolean; paused: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      {paused ? (
        <Pause size={10} style={{ color: '#f2cc60' }} />
      ) : connected ? (
        <Wifi size={10} style={{ color: '#3fb950' }} />
      ) : (
        <WifiOff size={10} style={{ color: '#ff7b72' }} />
      )}
      <span style={{
        fontSize: '9px', fontFamily: 'monospace', letterSpacing: '1px', fontWeight: 700,
        color: paused ? '#f2cc60' : connected ? '#3fb950' : '#ff7b72'
      }}>
        {paused ? 'PAUSED' : connected ? 'LIVE' : 'OFFLINE'}
      </span>
    </div>
  );
}

function EventRow({ event, expanded, onToggle }: {
  event: AuditEvent;
  expanded: boolean;
  onToggle: () => void;
}) {
  const meta = stageMeta(event.stage);
  const hasError = event.stage === 'error';

  return (
    <div
      onClick={onToggle}
      style={{
        display: 'flex', flexDirection: 'column',
        borderLeft: `2px solid ${expanded ? meta.color : 'transparent'}`,
        background: expanded ? meta.bg : 'transparent',
        borderBottom: '1px solid #161b22',
        cursor: 'pointer',
        transition: 'all 0.12s',
      }}
      onMouseEnter={e => { if (!expanded) (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.02)'; }}
      onMouseLeave={e => { if (!expanded) (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
    >
      {/* Main row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '7px 14px' }}>
        {/* timestamp */}
        <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#484f58', flexShrink: 0, width: '74px' }}>
          {formatTs(event.timestamp * 1000)}
        </span>

        {/* stage badge */}
        <span style={{
          fontSize: '9px', fontWeight: 700, fontFamily: 'monospace', letterSpacing: '0.5px',
          color: meta.color, flexShrink: 0, width: '86px'
        }}>
          {meta.symbol} {meta.label}
        </span>

        {/* agent */}
        <span style={{
          fontSize: '9px', color: '#6e7681', fontFamily: 'monospace',
          flexShrink: 0, width: '80px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
        }}>
          {event.agent}
        </span>

        {/* intention_id */}
        <span style={{ fontSize: '9px', color: '#30363d', fontFamily: 'monospace', flexShrink: 0 }}>
          #{event.intention_id?.slice(0, 8) ?? '--------'}
        </span>

        {/* data preview */}
        <span style={{
          fontSize: '10px', color: hasError ? '#ff7b72' : '#6e7681',
          fontFamily: 'monospace', flex: 1, overflow: 'hidden',
          textOverflow: 'ellipsis', whiteSpace: 'nowrap',
          fontWeight: hasError ? 600 : 400
        }}>
          {formatData(event.data)}
        </span>
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div style={{
          padding: '0 14px 12px 14px',
          borderTop: `1px solid ${meta.color}22`,
          marginTop: '0'
        }}>
          <pre style={{
            margin: 0, fontSize: '11px', lineHeight: 1.7,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            color: meta.color,
            background: '#010409',
            padding: '10px 12px',
            borderRadius: '4px',
            border: `1px solid ${meta.color}33`,
            overflowX: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all'
          }}>
            {JSON.stringify(event.data, null, 2)}
          </pre>
          <div style={{ marginTop: '6px', fontSize: '9px', color: '#484f58', fontFamily: 'monospace' }}>
            intention_id: {event.intention_id} · received: {formatTs(event.receivedAt)}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Metrics (tab console) ────────────────────────────────────────────────────

function MetricsGrid({ events }: { events: AuditEvent[] }) {
  const errors = events.filter(e => e.stage === 'error').length;
  const agents = [...new Set(events.map(e => e.agent))].length;
  const lastDuration = (() => {
    const resp = [...events].reverse().find(e => e.stage === 'response');
    return resp?.data?.duration ? `${(resp.data.duration as number).toFixed(2)}s` : '—';
  })();

  const metrics = [
    { label: 'Eventos totales', value: String(events.length), icon: <Activity size={13} />, color: '#58a6ff' },
    { label: 'Errores',         value: String(errors),         icon: <Zap size={13} />,      color: errors > 0 ? '#ff7b72' : '#3fb950' },
    { label: 'Agentes activos', value: String(agents),         icon: <Shield size={13} />,   color: '#d2a8ff' },
    { label: 'Última respuesta',value: lastDuration,            icon: <Database size={13} />, color: '#f2cc60' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '16px' }}>
      {metrics.map((m, i) => (
        <div key={i} style={{
          padding: '14px 16px', borderRadius: '10px',
          background: '#0d1117', border: '1px solid #21262d',
          display: 'flex', flexDirection: 'column', gap: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: m.color, opacity: 0.8 }}>
            {m.icon}
            <span style={{ fontSize: '9px', fontWeight: 700, letterSpacing: '0.5px', textTransform: 'uppercase', fontFamily: 'monospace' }}>{m.label}</span>
          </div>
          <div style={{ fontSize: '22px', fontFamily: 'monospace', fontWeight: 700, color: m.color, letterSpacing: '-1px' }}>{m.value}</div>
        </div>
      ))}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

const DeveloperConsole: React.FC<Props> = ({ onBack }) => {
  const [activeTab, setActiveTab]       = useState<Tab>('logs');
  const [events, setEvents]             = useState<AuditEvent[]>([]);
  const [connected, setConnected]       = useState(false);
  const [paused, setPaused]             = useState(false);
  const [filter, setFilter]             = useState<FilterLevel>('ALL');
  const [search, setSearch]             = useState('');
  const [expandedId, setExpandedId]     = useState<string | null>(null);
  const [autoScroll, setAutoScroll]     = useState(true);

  const esRef       = useRef<EventSource | null>(null);
  const bufferRef   = useRef<AuditEvent[]>([]); // buffer mientras pausado
  const bottomRef   = useRef<HTMLDivElement>(null);
  const counterRef  = useRef(0);

  // ── SSE connection ──────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
    }

    const es = new EventSource(SSE_URL);
    esRef.current = es;

    es.onopen = () => setConnected(true);

    es.onmessage = (e: MessageEvent) => {
      try {
        const raw = JSON.parse(e.data);
        const event: AuditEvent = {
          ...raw,
          id: `${++counterRef.current}-${Date.now()}`,
          receivedAt: Date.now(),
        };

        if (paused) {
          bufferRef.current.push(event);
          return;
        }

        setEvents(prev => {
          const next = [...prev, event];
          return next.length > MAX_EVENTS ? next.slice(next.length - MAX_EVENTS) : next;
        });
      } catch {
        // malformed event — ignorar
      }
    };

    es.onerror = () => {
      setConnected(false);
      es.close();
      // reconexión automática en 3s
      setTimeout(connect, 3000);
    };
  }, [paused]);

  useEffect(() => {
    connect();
    return () => {
      esRef.current?.close();
    };
  }, []); // solo al montar

  // ── Resume from pause ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!paused && bufferRef.current.length > 0) {
      setEvents(prev => {
        const next = [...prev, ...bufferRef.current];
        bufferRef.current = [];
        return next.length > MAX_EVENTS ? next.slice(next.length - MAX_EVENTS) : next;
      });
    }
  }, [paused]);

  // ── Auto-scroll ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (autoScroll && activeTab === 'logs') {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events, autoScroll, activeTab]);

  // ── Filtered events ─────────────────────────────────────────────────────────
  const filteredEvents = events.filter(ev => {
    if (filter !== 'ALL' && stageToFilterLevel(ev.stage as Stage) !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      const hit =
        ev.stage.includes(q) ||
        ev.agent.toLowerCase().includes(q) ||
        ev.intention_id?.includes(q) ||
        JSON.stringify(ev.data).toLowerCase().includes(q);
      if (!hit) return false;
    }
    return true;
  });

  // ── Handlers ─────────────────────────────────────────────────────────────────
  const toggleExpand = (id: string) =>
    setExpandedId(prev => (prev === id ? null : id));

  const clearEvents = () => {
    setEvents([]);
    bufferRef.current = [];
    setExpandedId(null);
  };

  // ─── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      background: '#010409', color: '#e6edf3',
      fontFamily: "'IBM Plex Mono', 'JetBrains Mono', monospace",
      height: '100%', overflow: 'hidden'
    }}>

      {/* ── HEADER ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 20px', borderBottom: '1px solid #21262d',
        background: '#0d1117', flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button onClick={onBack} title="Volver al panel" aria-label="Volver al panel" style={{
            background: 'none', border: 'none', color: '#58a6ff',
            cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px'
          }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, letterSpacing: '0.5px', color: '#e6edf3' }}>
              DEVELOPER <span style={{ color: '#388bfd' }}>CONSOLE</span>
            </div>
            <StreamBadge connected={connected} paused={paused} />
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {(['logs', 'console', 'architecture'] as Tab[]).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              background: activeTab === tab ? 'rgba(88,166,255,0.1)' : 'none',
              border: activeTab === tab ? '1px solid rgba(88,166,255,0.3)' : '1px solid transparent',
              borderRadius: '6px', color: activeTab === tab ? '#58a6ff' : '#484f58',
              fontSize: '9px', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase',
              padding: '4px 10px', cursor: 'pointer', fontFamily: 'inherit',
              transition: 'all 0.15s'
            }}>
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* ── CONTENT ── */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>

        {/* ── TAB: LOGS ── */}
        {activeTab === 'logs' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

            {/* Toolbar */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '8px 14px', borderBottom: '1px solid #161b22',
              background: '#0a0d12', flexShrink: 0, flexWrap: 'wrap'
            }}>
              {/* Filter pills */}
              {(['ALL', 'ERROR', 'WARN', 'INFO'] as FilterLevel[]).map(f => {
                const fColors: Record<FilterLevel, string> = { ALL: '#58a6ff', ERROR: '#ff7b72', WARN: '#f2cc60', INFO: '#3fb950' };
                return (
                  <button key={f} onClick={() => setFilter(f)} style={{
                    background: filter === f ? `${fColors[f]}18` : 'none',
                    border: `1px solid ${filter === f ? fColors[f] : '#21262d'}`,
                    borderRadius: '4px', color: filter === f ? fColors[f] : '#484f58',
                    fontSize: '9px', fontWeight: 700, letterSpacing: '0.5px',
                    padding: '2px 8px', cursor: 'pointer', fontFamily: 'inherit',
                    transition: 'all 0.12s'
                  }}>{f}</button>
                );
              })}

              {/* Search */}
              <div style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                background: '#161b22', border: '1px solid #30363d',
                borderRadius: '4px', padding: '3px 8px', flex: 1, minWidth: '120px'
              }}>
                <Search size={10} style={{ color: '#484f58', flexShrink: 0 }} />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="filtrar por stage, agent, id..."
                  style={{
                    background: 'none', border: 'none', outline: 'none',
                    color: '#8b949e', fontSize: '10px', fontFamily: 'inherit', width: '100%'
                  }}
                />
              </div>

              {/* Actions */}
              <button onClick={() => setPaused(p => !p)} style={{
                background: paused ? 'rgba(242,204,96,0.1)' : 'none',
                border: `1px solid ${paused ? '#f2cc60' : '#21262d'}`,
                borderRadius: '4px', color: paused ? '#f2cc60' : '#484f58',
                fontSize: '9px', padding: '2px 8px', cursor: 'pointer',
                fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: '4px',
                transition: 'all 0.12s'
              }}>
                {paused ? <Play size={9} /> : <Pause size={9} />}
                {paused ? `RESUME (${bufferRef.current.length})` : 'PAUSE'}
              </button>

              <button onClick={() => setAutoScroll(a => !a)} style={{
                background: autoScroll ? 'rgba(63,185,80,0.1)' : 'none',
                border: `1px solid ${autoScroll ? '#3fb950' : '#21262d'}`,
                borderRadius: '4px', color: autoScroll ? '#3fb950' : '#484f58',
                fontSize: '9px', padding: '2px 8px', cursor: 'pointer',
                fontFamily: 'inherit', transition: 'all 0.12s'
              }}>
                AUTO-SCROLL
              </button>

              <button onClick={clearEvents} style={{
                background: 'none', border: '1px solid #21262d',
                borderRadius: '4px', color: '#484f58', fontSize: '9px',
                padding: '2px 6px', cursor: 'pointer', fontFamily: 'inherit',
                display: 'flex', alignItems: 'center', gap: '4px',
                transition: 'all 0.12s'
              }}>
                <Trash2 size={9} /> CLEAR
              </button>

              <span style={{ fontSize: '9px', color: '#30363d', marginLeft: 'auto', fontFamily: 'monospace' }}>
                {filteredEvents.length}/{events.length} eventos
              </span>
            </div>

            {/* Column headers */}
            <div style={{
              display: 'flex', gap: '10px', padding: '4px 14px',
              borderBottom: '1px solid #161b22', background: '#0a0d12',
              flexShrink: 0
            }}>
              {[
                { label: 'TIME',    w: '74px' },
                { label: 'STAGE',   w: '86px' },
                { label: 'AGENT',   w: '80px' },
                { label: 'ID',      w: '80px' },
                { label: 'DATA',    w: 'auto' },
              ].map(col => (
                <span key={col.label} style={{
                  fontSize: '8px', color: '#21262d', fontWeight: 700,
                  letterSpacing: '1px', width: col.w, flexShrink: col.w === 'auto' ? 1 : 0,
                  flex: col.w === 'auto' ? 1 : undefined
                }}>{col.label}</span>
              ))}
            </div>

            {/* Events list */}
            <div style={{ flex: 1, overflowY: 'auto' }}
              onScroll={e => {
                const el = e.currentTarget;
                const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
                setAutoScroll(atBottom);
              }}
            >
              {filteredEvents.length === 0 ? (
                <div style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center',
                  justifyContent: 'center', padding: '60px 20px', gap: '12px', color: '#21262d'
                }}>
                  <Terminal size={32} style={{ opacity: 0.3 }} />
                  <span style={{ fontSize: '11px', letterSpacing: '1px' }}>
                    {connected ? 'Esperando eventos del sistema...' : 'Reconectando al stream...'}
                  </span>
                </div>
              ) : (
                filteredEvents.map(ev => (
                  <EventRow
                    key={ev.id}
                    event={ev}
                    expanded={expandedId === ev.id}
                    onToggle={() => toggleExpand(ev.id)}
                  />
                ))
              )}
              <div ref={bottomRef} />
            </div>
          </div>
        )}

        {/* ── TAB: CONSOLE ── */}
        {activeTab === 'console' && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
            <MetricsGrid events={events} />

            {/* Sandbox */}
            <div style={{
              borderRadius: '10px', background: '#0d1117',
              border: '1px solid #21262d', overflow: 'hidden', marginBottom: '16px'
            }}>
              <div style={{
                padding: '10px 14px', borderBottom: '1px solid #21262d',
                background: '#161b22', display: 'flex', alignItems: 'center', gap: '8px'
              }}>
                <Terminal size={12} style={{ color: '#58a6ff' }} />
                <span style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '1px', color: '#8b949e', textTransform: 'uppercase' }}>
                  Sandbox — Mandatos Crudos
                </span>
              </div>
              <div style={{ padding: '14px' }}>
                <div style={{
                  background: '#010409', padding: '10px 12px', borderRadius: '6px',
                  border: '1px solid #161b22', fontFamily: 'monospace', fontSize: '11px',
                  color: '#388bfd', minHeight: '80px', lineHeight: 1.8
                }}>
                  ALEGR-IA OS Developer Build · Sovereign Mode{'\n'}
                  Stream: {connected ? '● CONNECTED' : '○ RECONNECTING'} · Events: {events.length}
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                  <input
                    style={{
                      flex: 1, background: '#161b22', border: '1px solid #30363d',
                      borderRadius: '6px', padding: '8px 12px', color: '#e6edf3',
                      fontSize: '12px', fontFamily: 'inherit', outline: 'none'
                    }}
                    placeholder="inyectar_regla --strict --enforce-acsp"
                  />
                  <button style={{
                    background: 'linear-gradient(135deg, #1f6feb, #388bfd)',
                    border: 'none', borderRadius: '6px', color: '#fff',
                    padding: '8px 18px', cursor: 'pointer', fontSize: '11px',
                    fontFamily: 'inherit', fontWeight: 700, letterSpacing: '0.5px'
                  }}>RUN</button>
                </div>
              </div>
            </div>

            {/* Last errors summary */}
            {events.filter(e => e.stage === 'error').length > 0 && (
              <div style={{
                borderRadius: '10px', background: 'rgba(255,123,114,0.05)',
                border: '1px solid rgba(255,123,114,0.2)', overflow: 'hidden'
              }}>
                <div style={{
                  padding: '10px 14px', borderBottom: '1px solid rgba(255,123,114,0.15)',
                  display: 'flex', alignItems: 'center', gap: '8px'
                }}>
                  <span style={{ fontSize: '10px', fontWeight: 700, color: '#ff7b72', letterSpacing: '1px' }}>
                    ✘ ERRORES RECIENTES
                  </span>
                </div>
                <div style={{ padding: '8px 0' }}>
                  {events.filter(e => e.stage === 'error').slice(-5).reverse().map(ev => (
                    <div key={ev.id} style={{
                      padding: '6px 14px', borderBottom: '1px solid rgba(255,123,114,0.08)',
                      display: 'flex', gap: '12px', alignItems: 'flex-start'
                    }}>
                      <span style={{ fontSize: '9px', color: '#484f58', fontFamily: 'monospace', flexShrink: 0, marginTop: '2px' }}>
                        {formatTs(ev.timestamp * 1000)}
                      </span>
                      <span style={{ fontSize: '10px', color: '#ff7b72', fontFamily: 'monospace', flex: 1 }}>
                        [{ev.agent}] {ev.data?.error ?? formatData(ev.data)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── TAB: ARCHITECTURE ── */}
        {activeTab === 'architecture' && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            padding: '40px 20px', gap: '16px', textAlign: 'center'
          }}>
            {/* Flow diagram */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0', width: '100%', maxWidth: '340px' }}>
              {[
                { label: 'CHINEX', sub: 'Operador Soberano', color: '#388bfd', top: true },
                { label: 'NEXUS', sub: 'Orquestador / Contrato', color: '#d2a8ff' },
                { label: 'RADAR', sub: 'Detección — solo propone', color: '#79c0ff' },
                { label: 'ANIMA', sub: 'Traducción → Rol LLM', color: '#f2cc60' },
                { label: 'LLM', sub: 'Ejecución bajo contrato', color: '#3fb950' },
                { label: 'DEVELOPER', sub: 'Auditoría · Este panel', color: '#ff7b72', active: true },
              ].map((node, i, arr) => (
                <div key={node.label} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{
                    width: '100%', padding: '12px 20px',
                    background: node.active ? `${node.color}18` : '#0d1117',
                    border: `1px solid ${node.active ? node.color : '#21262d'}`,
                    borderRadius: i === 0 ? '10px 10px 0 0' : i === arr.length - 1 ? '0 0 10px 10px' : '0',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                  }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: node.color, letterSpacing: '0.5px' }}>
                      {node.label}
                    </span>
                    <span style={{ fontSize: '9px', color: '#484f58' }}>{node.sub}</span>
                  </div>
                  {i < arr.length - 1 && (
                    <div style={{ width: '1px', height: '0', borderLeft: '1px dashed #21262d' }} />
                  )}
                </div>
              ))}
            </div>

            <p style={{ fontSize: '10px', color: '#30363d', maxWidth: '320px', lineHeight: 1.7, marginTop: '8px' }}>
              El flujo es unidireccional. El humano valida en cada punto de cierre. Developer audita sin interferir.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeveloperConsole;
