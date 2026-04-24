import React, { useState, useEffect } from 'react';
import { 
  Database, Plus, Trash2, CheckCircle2, Globe, Cpu, Key, 
  Settings2, Activity, Shapes, Zap, ChevronDown, 
  ExternalLink, Power, LayoutGrid, List
} from 'lucide-react';
import { API_BASE } from '../core/config';

interface Provider {
  id: string;
  provider_type: string;
  alias: string;
  is_active: boolean;
  model: string;
  is_local: boolean;
  has_key: boolean;
  priority?: number;
}

const ProvidersBlock = () => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [activeTab, setActiveTab] = useState<'quick' | 'list'>('quick');
  const [expandedSection, setExpandedSection] = useState<string | null>('quick');
  const [newProvider, setNewProvider] = useState({
    provider: 'groq',
    api_key: '',
    alias: '',
    model: '',
    is_local: false
  });

  const fetchProviders = async () => {
    setSyncing(true);
    try {
      const res = await fetch(`${API_BASE}/providers`);
      const data = await res.json();
      setProviders(data.providers || []);
    } catch (err) {
      console.error('Error fetching providers:', err);
    } finally {
      setLoading(false);
      setTimeout(() => setSyncing(false), 1000);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const quickConnectProviders = [
    { id: 'ollama', name: 'Ollama Local', icon: <Cpu className="w-5 h-5" />, color: 'bg-slate-700/50', accent: 'text-amber-400', desc: 'Auto-detectar' },
    { id: 'gemini', name: 'Google Gemini', icon: <Zap className="w-5 h-5" />, color: 'bg-blue-600/20', accent: 'text-blue-400', desc: 'Link directo' },
    { id: 'groq', name: 'Groq Cloud', icon: <Activity className="w-5 h-5" />, color: 'bg-indigo-600/20', accent: 'text-indigo-400', desc: 'Link directo' },
    { id: 'fireworks', name: 'Fireworks AI', icon: <Shapes className="w-5 h-5" />, color: 'bg-purple-600/20', accent: 'text-purple-400', desc: 'Link directo' },
    { id: 'huggingface', name: 'Hugging Face', icon: <span className="text-xl">🤗</span>, color: 'bg-yellow-500/10', accent: 'text-yellow-400', desc: 'Link directo' },
    { id: 'openai', name: 'OpenAI', icon: <Zap className="w-5 h-5" />, color: 'bg-emerald-600/20', accent: 'text-emerald-400', desc: 'Link directo' },
    { id: 'anthropic', name: 'Anthropic Claude', icon: <Activity className="w-5 h-5" />, color: 'bg-orange-600/20', accent: 'text-orange-400', desc: 'Link directo' },
    { id: 'together', name: 'Together AI', icon: <Globe className="w-5 h-5" />, color: 'bg-blue-400/20', accent: 'text-blue-300', desc: 'Link directo' },
  ];

  const handleSelect = async (id: string) => {
    try {
      await fetch(`${API_BASE}/providers/select`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      fetchProviders();
    } catch (err) {
      console.error('Error selecting provider:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`${API_BASE}/providers/${id}`, {
        method: 'DELETE'
      });
      fetchProviders();
    } catch (err) {
      console.error('Error deleting provider:', err);
    }
  };

  const handleAdd = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAdding(true);
    try {
      const res = await fetch(`${API_BASE}/providers/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProvider)
      });
      const data = await res.json();
      if (data.status === 'ok') {
        setExpandedSection(null);
        setNewProvider({ provider: 'groq', api_key: '', alias: '', model: '', is_local: false });
        await fetchProviders();
      } else {
        alert(data.message || 'Error al agregar proveedor');
      }
    } catch (err) {
      console.error('Error adding provider:', err);
    } finally {
      setAdding(false);
    }
  };

  const selectQuickProvider = (id: string) => {
    setNewProvider({ ...newProvider, provider: id });
    setExpandedSection('add');
  };

  return (
    <div className="flex flex-col h-full bg-[#08090a] border border-white/5 rounded-3xl overflow-hidden shadow-2xl animate-fade-in font-display text-slate-200">
      
      {/* Header Premium */}
      <div className="p-6 bg-gradient-to-r from-slate-900 to-black border-b border-white/5">
        <div className="flex items-center gap-4 mb-1">
          <div className="w-10 h-10 bg-indigo-600/20 rounded-xl flex items-center justify-center text-indigo-400 shadow-glow-sm">
            <Globe size={24} />
          </div>
          <div>
            <h3 className="text-xl font-bold tracking-tight text-white uppercase">Configuración de APIs</h3>
            <p className="text-xs text-slate-500 font-medium">Gestiona tus conexiones a la Inteligencia Artificial</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
        
        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'ACTIVOS', val: providers.filter(p => p.is_active).length, color: 'text-emerald-400' },
            { label: 'MODELOS TEXTO', val: providers.length, color: 'text-blue-400' },
            { label: 'MODELOS VISIÓN', val: providers.filter(p => p.model && (p.model.toLowerCase().includes('vision') || p.model.toLowerCase().includes('gpt-4o') || p.model.toLowerCase().includes('gemini-1.5') || p.model.toLowerCase().includes('gemini-2') || p.model.toLowerCase().includes('claude-3'))).length, color: 'text-purple-400' }
          ].map((stat, i) => (
            <div key={i} className="bg-white/5 border border-white/5 rounded-2xl p-4 flex flex-col justify-center">
              <span className="text-[10px] font-bold text-slate-500 tracking-widest mb-1 italic">{stat.label}</span>
              <span className={`text-2xl font-bold ${stat.color}`}>{stat.val}</span>
            </div>
          ))}
        </div>
        
        {/* Cascade Mode Toggle */}
        <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-2xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 bg-indigo-500/20 rounded-lg flex items-center justify-center text-indigo-400">
                <Database size={16} />
             </div>
             <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">Cascada de Inteligencia</h4>
                <p className="text-[10px] text-indigo-300/60 font-medium">Pool de cuentas redundantes activo</p>
             </div>
          </div>
          <div className="bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full text-[10px] font-bold border border-emerald-500/20 animate-pulse">
             POOL DINÁMICO ACTIVADO
          </div>
        </div>

        {/* Quick Connect Section */}
        <div className="bg-white/5 border border-white/5 rounded-2xl overflow-hidden">
          <button 
            onClick={() => setExpandedSection(expandedSection === 'quick' ? null : 'quick')}
            className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Zap className="text-amber-400" size={16} />
              <span className="text-xs font-bold uppercase tracking-widest">Quick Connect</span>
              <span className="text-[10px] text-slate-500 lowercase ml-2">Conecta en 1 click</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${expandedSection === 'quick' ? 'rotate-180' : ''}`} />
          </button>
          
          {expandedSection === 'quick' && (
            <div className="p-5 grid grid-cols-2 lg:grid-cols-3 gap-3 animate-fade-in">
              {quickConnectProviders.map((p: any) => (
                <div 
                  key={p.id} 
                  onClick={() => selectQuickProvider(p.id)}
                  className="group relative bg-black/40 border border-white/5 rounded-xl p-4 hover:border-indigo-500/30 hover:bg-indigo-500/5 transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-8 h-8 ${p.color} ${p.accent} rounded-lg flex items-center justify-center`}>
                      {p.icon}
                    </div>
                    {providers.some(pr => pr.provider_type === p.id) && (
                      <CheckCircle2 size={12} className="text-emerald-500" />
                    )}
                    <ExternalLink size={10} className="text-slate-700 group-hover:text-slate-400 transition-colors" />
                  </div>
                  <h4 className="text-xs font-bold text-white mb-0.5">{p.name}</h4>
                  <p className="text-[9px] text-slate-600 uppercase tracking-tighter">{p.desc}</p>
                </div>
              ))}
              <div className="col-span-full mt-4 flex items-center justify-center gap-2 py-2">
                 <div className="w-1 h-1 bg-amber-400 rounded-full"></div>
                 <p className="text-[9px] text-slate-500 italic">Los proveedores conectados se agregan automáticamente a la cascada de IA</p>
              </div>
            </div>
          )}
        </div>

        {/* Manual Add Section */}
        <div className="bg-white/5 border border-white/5 rounded-2xl overflow-hidden">
          <button 
            onClick={() => setExpandedSection(expandedSection === 'add' ? null : 'add')}
            className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Plus className="text-emerald-400" size={16} />
              <span className="text-xs font-bold uppercase tracking-widest">Agregar Proveedor</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${expandedSection === 'add' ? 'rotate-180' : ''}`} />
          </button>
          
          {expandedSection === 'add' && (
            <div className="p-6 space-y-5 animate-fade-in border-t border-white/5">
              <form onSubmit={handleAdd} className="space-y-5">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-slate-500 uppercase font-bold tracking-widest ml-1">Motor / ID</label>
                    <input 
                      list="ai-engines"
                      placeholder="Ej: groq, openai..."
                      className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white outline-none focus:border-indigo-500/50"
                      value={newProvider.provider}
                      onChange={e => setNewProvider({...newProvider, provider: e.target.value})}
                      required
                    />
                    <datalist id="ai-engines">
                      <option value="groq" />
                      <option value="openai" />
                      <option value="gemini" />
                      <option value="claude" />
                      <option value="ollama" />
                    </datalist>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-slate-500 uppercase font-bold tracking-widest ml-1">Alias</label>
                    <input 
                      placeholder="Mi Conexión"
                      className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white outline-none focus:border-indigo-500/50"
                      value={newProvider.alias}
                      onChange={e => setNewProvider({...newProvider, alias: e.target.value})}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] text-slate-500 uppercase font-bold tracking-widest ml-1">Modelo Principal</label>
                    <input 
                      placeholder="Ej: gpt-4o, llama-3..."
                      className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white outline-none focus:border-indigo-500/50"
                      value={newProvider.model}
                      onChange={e => setNewProvider({...newProvider, model: e.target.value})}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="space-y-1.5">
                      <label className="text-[10px] text-slate-500 uppercase font-bold tracking-widest ml-1">Endpoint (Opcional)</label>
                      <input 
                        placeholder="https://api.custom.com/v1"
                        className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white outline-none focus:border-indigo-500/50"
                        value={(newProvider as any).endpoint || ''}
                        onChange={e => setNewProvider({...newProvider, ...{ endpoint: e.target.value } as any })}
                      />
                   </div>
                   <div className="flex flex-col justify-end pb-1 px-1">
                      <label className="flex items-center gap-3 cursor-pointer group">
                        <div className="relative">
                          <input 
                            type="checkbox" 
                            className="sr-only peer"
                            checked={newProvider.is_local}
                            onChange={e => setNewProvider({...newProvider, is_local: e.target.checked})}
                          />
                          <div className="w-10 h-5 bg-white/5 border border-white/10 rounded-full peer peer-checked:bg-emerald-600 transition-all"></div>
                          <div className="absolute top-1 left-1 w-3 h-3 bg-slate-500 rounded-full peer-checked:translate-x-5 peer-checked:bg-white transition-all"></div>
                        </div>
                        <span className="text-[10px] font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-widest">Servidor Local / No Validar Key</span>
                      </label>
                   </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-500 uppercase font-bold tracking-widest ml-1">API Key / Token</label>
                  <div className="relative">
                    <Key className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600" size={14} />
                    <input 
                      type="password"
                      placeholder="sk-........................" 
                      className="w-full bg-black/50 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-xs text-white font-mono outline-none focus:border-indigo-500/50"
                      value={newProvider.api_key}
                      onChange={e => setNewProvider({...newProvider, api_key: e.target.value})}
                      required={!newProvider.is_local}
                    />
                  </div>
                </div>
                <button 
                  type="submit"
                  disabled={adding}
                  className={`w-full py-3 ${adding ? 'bg-slate-700 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500'} text-white rounded-xl text-xs font-bold uppercase transition-all shadow-lg shadow-indigo-600/10 active:scale-95 flex items-center justify-center gap-2`}
                >
                  {adding ? (
                    <>
                      <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                      Validando Conexión...
                    </>
                  ) : (
                    'Conectar Proveedor'
                  )}
                </button>
              </form>
            </div>
          )}
        </div>

        {/* Active Providers List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Proveedores Activos</span>
              {syncing && <div className="w-2 h-2 bg-indigo-500 rounded-full animate-ping"></div>}
            </div>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => fetchProviders()}
                className="p-1.5 text-slate-500 hover:text-indigo-400 transition-colors"
                title="Sincronizar ahora"
              >
                <Database size={12} className={syncing ? 'animate-spin' : ''} />
              </button>
              <div className="flex bg-white/5 rounded-lg p-1">
                <button 
                  title="Vista Cuadrícula"
                  onClick={() => setActiveTab('quick')} 
                  className={`p-1 rounded ${activeTab === 'quick' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-600'}`}
                >
                  <LayoutGrid size={12} />
                </button>
                <button 
                  title="Vista Lista"
                  onClick={() => setActiveTab('list')} 
                  className={`p-1 rounded ${activeTab === 'list' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-600'}`}
                >
                  <List size={12} />
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {providers.sort((a,b) => (a.priority || 99) - (b.priority || 99)).map(p => (
              <div key={p.id} className="bg-white/5 border border-white/5 rounded-2xl p-4 flex items-center justify-between group">
                <div className="flex items-center gap-4">
                   <div className={`w-12 h-12 bg-black rounded-xl flex items-center justify-center border ${p.is_active ? 'border-indigo-500/50' : 'border-white/5'}`}>
                      <div className={`w-6 h-6 flex items-center justify-center rounded ${p.is_active ? 'text-indigo-400' : 'text-slate-600'}`}>
                        {p.is_local ? <Cpu size={18} /> : <Zap size={18} />}
                      </div>
                   </div>
                   <div>
                      <h4 className="text-sm font-bold text-white mb-0.5">{p.alias}</h4>
                      <div className="flex items-center gap-2">
                        <p className="text-[10px] text-slate-500 font-mono tracking-tighter uppercase">{p.model}</p>
                        <span className="text-slate-700">•</span>
                        <div className="flex items-center gap-1.5 bg-black/40 px-2 py-0.5 rounded border border-white/5">
                           <span className="text-[8px] text-slate-500 font-bold uppercase tracking-tighter">Prio</span>
                           <input 
                             type="number" 
                             defaultValue={p.priority || 10}
                             title="Prioridad del proveedor"
                             aria-label="Prioridad del proveedor"
                             placeholder="10"
                             onBlur={async (e) => {
                               const val = parseInt(e.target.value);
                               if (val === p.priority) return;
                               await fetch(`${API_BASE}/providers/${p.id}/priority`, {
                                 method: 'PATCH',
                                 headers: { 'Content-Type': 'application/json' },
                                 body: JSON.stringify({ priority: val })
                               });
                               fetchProviders();
                             }}
                             className="w-8 bg-transparent text-[10px] font-bold text-indigo-400 outline-none"
                           />
                        </div>
                      </div>
                   </div>
                </div>
                <div className="flex items-center gap-2">
                   <div 
                     className={`p-2 rounded-xl transition-all cursor-pointer ${p.is_active ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'bg-slate-800 text-slate-500'}`} 
                     onClick={async () => {
                        await fetch(`${API_BASE}/providers/toggle`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ id: p.id, active: !p.is_active })
                        });
                        fetchProviders();
                     }}
                     title={p.is_active ? "Desactivar de cascada" : "Activar para pool"}
                   >
                      <Power size={14} />
                   </div>
                   <div className="p-2 rounded-xl bg-slate-800 text-slate-500 hover:text-white cursor-pointer transition-all">
                      <Settings2 size={14} />
                   </div>
                   <div className="p-2 rounded-xl bg-slate-800 text-slate-500 hover:text-red-400 cursor-pointer transition-all opacity-0 group-hover:opacity-100" onClick={() => handleDelete(p.id)}>
                      <Trash2 size={14} />
                   </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Footer System Status */}
      <div className="p-4 bg-black/50 border-t border-white/5 flex items-center justify-between text-[9px] uppercase font-bold tracking-widest text-slate-600 italic">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          <span>Núcleo Sincronizado</span>
        </div>
        <span>ALEGR-IA OS v.1.0</span>
      </div>
    </div>
  );
};

export default ProvidersBlock;
