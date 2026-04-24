import React from 'react';
import {
  Home, FolderOpen,
  Sparkles, ScanSearch, Palette, Wrench, FlaskConical, Newspaper, Video, Eye,
  Database, Globe, Code2, BookOpen, Shield,
  BarChart3, Bot, ShoppingBag, Package, Zap,
  Settings as SettingsIcon
} from 'lucide-react';

/**
 * Navigation categories shared between SidebarComp and App.
 * Kept in a separate file so SidebarComp.jsx only exports a component,
 * which is required for Vite Fast Refresh to work correctly.
 */
export const categories = [
  {
    title: 'ECOSISTEMA',
    items: [
      { id: 'mando',     name: 'Centro de Mando', icon: <Home size={17} />,       description: 'Resumen operativo del sistema.' },
      { id: 'anima_chat',name: 'Anima (Chat)',     icon: <Bot size={17} />,        description: 'Interacción directa con la inteligencia central.' },
      { id: 'projects',  name: 'Proyectos',        icon: <FolderOpen size={17} />, description: 'Gestión de proyectos activos.' },
    ]
  },
  {
    title: 'CREACIÓN Y MARCA',
    items: [
      { id: 'genesis',      name: 'Génesis (Semilla)',     icon: <Sparkles size={17} />,   description: 'Gestación de universos conceptuales.' },
      { id: 'brand_scanner',name: 'Brand Scanner',         icon: <ScanSearch size={17} />, description: 'Análisis y escaneo de marca.' },
      { id: 'brand_studio', name: 'Brand Studio',          icon: <Palette size={17} />,    description: 'Identidad y diseño de marca.' },
      { id: 'taller',       name: 'Taller Generativo',     icon: <Wrench size={17} />,     description: 'Espacio de creación libre.' },
      { id: 'anima_forge',  name: 'Anima Forge',           icon: <FlaskConical size={17}/>, description: 'Prototipos e iteración rápida.' },
      { id: 'content',      name: 'Content Machine',       icon: <Newspaper size={17} />,  description: 'Generación de contenido AI.' },
      { id: 'video_hub',    name: 'Video AI Hub',          icon: <Video size={17} />,      description: 'Producción de video con IA.' },
      { id: 'veoscope',     name: 'VEOScope (Video)',      icon: <Eye size={17} />,        description: 'Análisis visual clínico.' },
    ]
  },
  {
    title: 'INTELIGENCIA DE SISTEMAS',
    items: [
      { id: 'nexus_prime', name: 'Nexus Prime (Deep Dive)', icon: <Database size={17} />, description: 'Memoria e identidad digital.' },
      { id: 'nexus',       name: 'Nexus (Governance)',       icon: <Shield size={17} />,   description: 'Configuración interna y preferencias.' },
      { id: 'radar',       name: 'Radar (Trends/Prompts)',   icon: <Globe size={17} />,    description: 'Investigación y tendencias.' },
      { id: 'developer',   name: 'Developer',               icon: <Code2 size={17} />,    description: 'IDE soberano integrado.' },
      { id: 'noticias',    name: 'Noticias Contextual',     icon: <BookOpen size={17} />, description: 'Contexto informativo AI.' },
    ]
  },
  {
    title: 'ESTRATEGIA Y CONTROL',
    items: [
      { id: 'crm',         name: 'CRM & Negocio',  icon: <BarChart3 size={17} />,   description: 'Clientes y pipeline comercial.' },
      { id: 'app_agent',   name: 'App Agent',       icon: <Bot size={17} />,         description: 'Agente autónomo de apps.' },
      { id: 'marketplace', name: 'Marketplace',     icon: <ShoppingBag size={17} />, description: 'Ecosistema de recursos.' },
      { id: 'api_installer',name: 'API Installer',  icon: <Package size={17} />,     description: 'Instalación de integraciones.' },
      { id: 'mithick',     name: 'Mithick Prime',   icon: <Zap size={17} />,         description: 'Motor de estrategia avanzada.' },
    ]
  },
  {
    title: 'CONFIGURACIÓN Y ESTADO',
    items: [
      { id: 'settings', name: 'Ajustes', icon: <SettingsIcon size={17} />, description: 'Kernel, APIs y configuración.' },
    ]
  }
];
