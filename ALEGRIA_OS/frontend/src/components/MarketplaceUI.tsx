import React, { useState } from 'react';
import { ShoppingBag, Search, Filter, Star, Download, ShieldCheck, Cpu, Database, Palette, Globe } from 'lucide-react';

interface APIProduct {
  id: string;
  name: string;
  description: string;
  category: string;
  price: string;
  rating: number;
  icon: React.ReactNode;
}

const PRODUCTS: APIProduct[] = [
  {
    id: 'uni-list',
    name: 'Universities List',
    description: 'List of universities and domains.',
    category: 'Data',
    price: 'FREE',
    rating: 4.5,
    icon: <Database size={20} />,
  },
  {
    id: 'vision-ai',
    name: 'Vision Core',
    description: 'Sovereign image recognition API.',
    category: 'AI',
    price: 'PREMIUM',
    rating: 4.9,
    icon: <Cpu size={20} />,
  },
  {
    id: 'brand-kit',
    name: 'Auto Brand Kit',
    description: 'Instant brand identity generation.',
    category: 'Media',
    price: '$ 12 / mo',
    rating: 4.7,
    icon: <Palette size={20} />,
  },
];

const CATEGORIES = ['All', 'AI', 'Development', 'Data', 'Media', 'Finance'];

export default function MarketplaceUI() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117] h-full overflow-hidden">
      {/* Header */}
      <div className="px-10 pt-12 pb-10 border-b border-white/5">
        <h1 className="text-4xl font-black text-white tracking-tight mb-2">API Marketplace</h1>
        <p className="text-slate-500 text-[15px] font-medium max-w-2xl">
          Explora, conecta y potencia tu ecosistema con APIs listas para usar.
        </p>

        <div className="flex gap-4 mt-8">
          <div className="flex-1 relative">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
            <input 
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar APIs (ej: Vision, NLP, Crypto, Weather)..."
              className="w-full bg-[#161b22] border border-white/[0.08] rounded-2xl pl-14 pr-6 py-4 text-[15px] text-white placeholder-slate-600 outline-none focus:border-purple-500/40 transition-all"
            />
          </div>
          <button className="flex items-center gap-3 px-6 bg-[#1c2330] border border-white/10 rounded-2xl text-slate-300 hover:text-white hover:bg-white/5 transition-all group">
            <Filter size={18} className="text-slate-500 group-hover:text-purple-400" />
            <span className="text-sm font-bold uppercase tracking-widest">Filtros</span>
          </button>
        </div>

        <div className="flex gap-2 mt-8">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-6 py-2 rounded-full text-[12px] font-black uppercase tracking-wider transition-all ${
                activeCategory === cat 
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' 
                  : 'bg-white/5 text-slate-500 hover:text-slate-300 hover:bg-white/10'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-10 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {PRODUCTS.filter(p => activeCategory === 'All' || p.category === activeCategory).map((product) => (
            <div 
              key={product.id}
              className="bg-[#161b22] border border-white/[0.08] rounded-[28px] p-6 hover:border-white/20 hover:bg-[#1c2330] transition-all group flex flex-col"
            >
              <div className="flex items-start justify-between mb-6">
                <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-slate-400 group-hover:text-white transition-colors border border-white/10">
                  {product.icon}
                </div>
                <div className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${
                  product.price === 'FREE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                }`}>
                  {product.price}
                </div>
              </div>

              <h3 className="text-white font-bold text-lg mb-1">{product.name}</h3>
              <p className="text-slate-500 text-[13px] leading-relaxed mb-8 flex-1">
                {product.description}
              </p>

              <div className="flex items-center justify-between pt-5 border-t border-white/5">
                <div className="flex items-center gap-1.5">
                   <div className="flex gap-0.5">
                     {[...Array(5)].map((_, i) => (
                       <Star key={i} size={10} className={i < Math.floor(product.rating) ? 'text-amber-400 fill-amber-400' : 'text-slate-700'} />
                     ))}
                   </div>
                   <span className="text-[10px] font-bold text-slate-500 mt-0.5">{product.rating}</span>
                </div>
                <button className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors">
                   <Download size={14} />
                   <span className="text-[10px] font-black uppercase tracking-widest">Connect</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
