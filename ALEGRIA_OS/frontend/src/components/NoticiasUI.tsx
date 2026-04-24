import React, { useState, useEffect } from 'react';
import { 
  Newspaper, Globe, ExternalLink, RefreshCw, Radio, 
  Search, BookOpen, Layers, Zap, ArrowLeft, Maximize2,
  TrendingUp, Clock, ChevronRight, CloudRain, Wind, Droplets,
  Loader2
} from 'lucide-react';

interface NewsCard {
  id: string;
  category: string;
  title: string;
  image: string;
  source: string;
  time: string;
  link: string;
  size?: 'large' | 'medium' | 'small';
}

interface WeatherData {
  temp: number | string;
  condition: string;
  city: string;
  wind?: number;
  forecast?: Array<{ day: string; max: number; min: number; code: number }>;
}

export default function NoticiasUI() {
  const [activeTab, setActiveTab] = useState('general');
  const [news, setNews] = useState<NewsCard[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  const tabs = [
    { id: 'general', label: 'Descubrir' },
    { id: 'deportes', label: 'Deportes' },
    { id: 'tecnologia', label: 'Tecnología' },
    { id: 'dinero', label: 'Dinero' },
    { id: 'tiempo', label: 'Tiempo' }
  ];

  const fetchDashboard = async (cat: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/noticias/dashboard?category=${cat}`);
      const data = await response.json();
      if (data.status === 'ok') {
        // Adaptar noticias del RSS al formato de cards
        const adaptedNews = data.news.map((item: any, index: number) => ({
          id: item.id,
          category: cat.toUpperCase(),
          title: item.title,
          image: item.image,
          source: item.source,
          time: item.time,
          link: item.link,
          size: index === 0 ? 'large' : (index < 5 ? 'medium' : 'small')
        }));
        setNews(adaptedNews);
        setWeather(data.weather);
      }
    } catch (error) {
      console.error("Error fetching news dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard(activeTab);
  }, [activeTab]);

  if (loading && news.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0b141a] text-white">
        <Loader2 size={40} className="animate-spin text-purple-500 mb-4" />
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">Sincronizando Feed Global...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-[#0b141a] h-full overflow-hidden animate-fade-in font-sans">
      
      {/* NAVEGACIÓN SUPERIOR ESTILO MSN */}
      <div className="px-10 py-4 bg-[#111b21] border-b border-white/5 flex items-center justify-between z-30">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-tr from-blue-500 via-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white font-black text-xs">
              msn
            </div>
          </div>
          
          <nav className="flex items-center gap-6">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`text-[13px] font-bold transition-all hover:text-white ${
                  activeTab === tab.id ? 'text-white border-b-2 border-white pb-1' : 'text-slate-400'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative group">
            <input 
              type="text" 
              placeholder="Buscar en la web" 
              className="bg-[#1f2c34] border border-white/10 rounded-full py-1.5 px-10 text-[12px] text-white w-64 focus:ring-2 focus:ring-purple-500/50 outline-none transition-all"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
          </div>
          <button 
            onClick={() => fetchDashboard(activeTab)}
            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-all text-slate-400 hover:text-white"
            title="Actualizar Noticias"
            aria-label="Actualizar Noticias"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* DASHBOARD DE NOTICIAS GRID */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-10 bg-[#0b141a]">
        <div className="max-w-[1400px] mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 auto-rows-[200px]">
          
          {/* FEATURED LARGE CARD (Col: 1, Row: Span 2) */}
          {news[0] && (
            <a 
              href={news[0].link} 
              target="_blank" 
              rel="noopener noreferrer"
              className="md:col-span-2 md:row-span-2 group relative rounded-[24px] overflow-hidden border border-white/5 shadow-2xl"
            >
              <img 
                src={news[0].image} 
                alt={news[0].title}
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 p-8 w-full">
                <span className="inline-block px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-[10px] font-black text-white uppercase tracking-widest mb-3">
                  {news[0].category}
                </span>
                <h2 className="text-3xl font-black text-white mb-4 leading-tight group-hover:text-purple-300 transition-colors">
                  {news[0].title}
                </h2>
                <div className="flex items-center gap-3 text-slate-400 text-[11px] font-bold">
                  <span>{news[0].source}</span>
                  <span>•</span>
                  <span className="line-clamp-1">{news[0].time}</span>
                </div>
              </div>
            </a>
          )}

          {/* MEDIUM CARDS */}
          {news.slice(1, 3).map((item) => (
            <a 
              key={item.id}
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              className="group relative rounded-[24px] overflow-hidden border border-white/5 bg-[#162129] flex flex-col"
            >
              <div className="h-2/5 overflow-hidden">
                 <img src={item.image} alt={item.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              </div>
              <div className="p-5 flex-1 flex flex-col">
                 <div className="flex items-center gap-2 mb-2">
                   <span className="text-[10px] text-slate-500 font-bold">{item.source} • {item.time.split(',')[0]}</span>
                 </div>
                 <h3 className="text-sm font-bold text-white group-hover:text-purple-400 transition-colors line-clamp-3">
                   {item.title}
                 </h3>
              </div>
            </a>
          ))}

          {/* RIGHT COLUMN HIGHLIGHT */}
          {news[3] && (
            <a 
              href={news[3].link}
              target="_blank"
              rel="noopener noreferrer"
              className="md:row-span-2 group relative rounded-[24px] overflow-hidden border border-white/5 shadow-xl"
            >
               <img src={news[3].image} alt={news[3].title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
               <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
               <div className="absolute bottom-0 left-0 p-6">
                  <h3 className="text-base font-black text-white leading-tight mb-2 group-hover:text-blue-400 transition-colors">
                    {news[3].title}
                  </h3>
                  <span className="text-[10px] text-slate-400 font-bold">{news[3].source}</span>
               </div>
            </a>
          )}

          {/* NEWS FEED LIST */}
          <div className="md:col-span-1 md:row-span-2 bg-[#162129] rounded-[24px] border border-white/5 p-6 flex flex-col gap-6">
             <div className="flex items-center justify-between border-b border-white/5 pb-4">
                <h4 className="text-[10px] font-black text-orange-500 uppercase tracking-widest flex items-center gap-2">
                   <Zap size={14} /> Historias principales
                </h4>
             </div>
             {news.slice(4, 7).map((n, i) => (
               <a 
                 key={n.id} 
                 href={n.link}
                 target="_blank"
                 rel="noopener noreferrer"
                 className="space-y-1 group cursor-pointer"
               >
                  <div className="flex items-center gap-2 text-[9px] font-bold text-slate-500">
                     <span className="text-white">{n.source}</span>
                     <span>•</span>
                     <span className="line-clamp-1">{n.time.split(',')[0]}</span>
                  </div>
                  <p className="text-[12px] text-slate-300 font-bold group-hover:text-white transition-colors leading-relaxed line-clamp-3">
                    {n.title}
                  </p>
               </a>
             ))}
          </div>

          {/* MORE CARDS */}
          {news.slice(7, 9).map((item) => (
            <a 
              key={item.id}
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              className="md:col-span-1 group relative rounded-[24px] overflow-hidden border border-white/5 bg-[#162129] flex flex-col"
            >
              <div className="h-2/5 overflow-hidden">
                 <img src={item.image} alt={item.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              </div>
              <div className="p-5">
                 <h3 className="text-sm font-black text-white group-hover:text-purple-400 transition-colors line-clamp-2">
                   {item.title}
                 </h3>
              </div>
            </a>
          ))}

          {/* WEATHER WIDGET (Real Data) */}
          {weather && (
            <div className="group relative rounded-[24px] overflow-hidden border border-white/5 bg-gradient-to-br from-blue-600/40 via-indigo-600/20 to-transparent p-6 flex flex-col">
               <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-black text-white uppercase tracking-widest flex items-center gap-2">
                     <Globe size={14} /> {weather.city}
                  </span>
                  <span className="text-[10px] font-bold text-white/50">{weather.temp}°C</span>
               </div>
               
               <div className="flex-1 flex items-center justify-center">
                  <div className="flex flex-col items-center">
                     <CloudRain size={48} className="text-blue-400 animate-pulse" />
                     <span className="text-3xl font-black text-white mt-2">{weather.temp}°</span>
                     <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{weather.condition}</span>
                  </div>
               </div>

               {weather.forecast && (
                 <div className="flex justify-between mt-4 border-t border-white/5 pt-4">
                    {weather.forecast.map((f, i) => (
                      <div key={i} className="flex flex-col items-center">
                         <span className="text-[8px] font-bold text-slate-500 uppercase">{f.day}</span>
                         <span className="text-[11px] font-bold text-white">{f.max}°</span>
                         <CloudRain size={12} className="text-blue-400 mt-1" />
                      </div>
                    ))}
                 </div>
               )}
            </div>
          )}

        </div>

        {/* FOOTER DE EXPLORACIÓN */}
        <div className="max-w-[1400px] mx-auto mt-12 mb-20 text-center">
           <button className="px-10 py-4 bg-white/5 hover:bg-white/10 rounded-full border border-white/10 text-[11px] font-black text-slate-400 hover:text-white transition-all uppercase tracking-[0.3em] flex items-center gap-3 mx-auto">
             Explorar más en la web
             <ChevronRight size={16} />
           </button>
        </div>
      </div>

      {/* FOOTER BAR */}
      <div className="px-10 py-5 border-t border-white/5 bg-black/40 flex justify-between items-center text-slate-600">
        <div className="flex items-center gap-2">
          <Radio size={12} className="text-emerald-500 animate-pulse" />
          <span className="text-[9px] font-black uppercase tracking-widest">Global Intelligence Feed · Sovereign Awareness</span>
        </div>
        <div className="flex gap-4">
          <span className="text-[9px] font-bold">FEEDS_STABLE: 100%</span>
        </div>
      </div>
    </div>
  );
}
