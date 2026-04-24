import React, { useState, useEffect } from 'react';
import { registry, UIBlock } from '../core/UIRegistry';
import { Move, Copy, Trash2, Plus } from 'lucide-react';

interface LayoutItem {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export default function DynamicWorkspace() {
  const [blocks, setBlocks] = useState<UIBlock[]>([]);
  const [layout, setLayout] = useState<LayoutItem[]>(() => {
    const saved = localStorage.getItem('alegria_layout');
    return saved ? JSON.parse(saved) : [];
  });
  const [draggedId, setDraggedId] = useState<string | null>(null);

  useEffect(() => {
    setBlocks(registry.getAllBlocks());
    return registry.subscribe(() => {
      setBlocks(registry.getAllBlocks());
    });
  }, []);

  useEffect(() => {
    localStorage.setItem('alegria_layout', JSON.stringify(layout));
  }, [layout]);

  const handleDragStart = (e: React.DragEvent<HTMLElement>, id: string) => {
    setDraggedId(id);
    e.dataTransfer.setData('text/plain', id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDrop = (e: React.DragEvent<HTMLElement>) => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    const workspace = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - workspace.left;
    const y = e.clientY - workspace.top;

    setLayout(prev => {
      const existing = prev.find(item => item.id === id);
      if (existing) {
        return prev.map(item => item.id === id ? { ...item, x, y } : item);
      }
      return [...prev, { id, x, y, w: 300, h: 200 }];
    });
    setDraggedId(null);
  };

  const handleClone = (id: string) => {
    const clone = registry.clone(id);
    if (clone) {
      const parentLayout = layout.find(l => l.id === id);
      if (parentLayout) {
        setLayout(prev => [...prev, { ...parentLayout, id: clone.id, x: parentLayout.x + 20, y: parentLayout.y + 20 }]);
      }
    }
  };

  const handleRemove = (id: string) => {
    setLayout(prev => prev.filter(l => l.id !== id));
  };

  return (
    <div 
      className="flex-1 bg-slate-950 relative overflow-hidden workspace-grid"
      onDragOver={(e: React.DragEvent<HTMLElement>) => e.preventDefault()}
      onDrop={handleDrop}
    >
      {/* Barra de Herramientas del Registro */}
      <div className="absolute top-4 left-4 z-50 flex gap-2">
         {blocks.filter(b => !layout.find(l => l.id === b.id)).map(block => (
           <div 
             key={block.id}
             draggable
             onDragStart={(e: React.DragEvent<HTMLElement>) => handleDragStart(e, block.id)}
             className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-full text-xs font-bold text-slate-300 cursor-grab hover:bg-slate-700 active:cursor-grabbing flex items-center gap-2 shadow-xl"
           >
             <Plus size={14} /> {block.name}
           </div>
         ))}
      </div>

      {/* Espacio de Trabajo */}
      {layout.map((item) => {
        const block = blocks.find(b => b.id === item.id);
        if (!block) return null;
        
        const Component = block.component;
        
        return (
          <WorkspaceBlock 
            key={item.id}
            item={item}
            block={block}
            dragged={draggedId === item.id}
            onDragStart={handleDragStart}
            onClone={() => handleClone(item.id)}
            onRemove={() => handleRemove(item.id)}
          />
        );
      })}

      {/* Indicador de Espacio Vacío */}
      {layout.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-slate-600 animate-pulse">
          <Move size={48} className="mb-4" />
          <p className="font-serif italic text-xl">Arrastrá bloques desde la parte superior para componer tu UI</p>
        </div>
      )}
    </div>
  );
}

interface WorkspaceBlockProps {
  item: LayoutItem;
  block: UIBlock;
  dragged: boolean;
  onDragStart: (e: React.DragEvent<HTMLElement>, id: string) => void;
  onClone: () => void;
  onRemove: () => void;
}

// --- SUB-COMPONENT CON POSICIONAMIENTO IMPERATIVO ---
const WorkspaceBlock = ({ item, block, dragged, onDragStart, onClone, onRemove }: WorkspaceBlockProps) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const Component = block.component;

  React.useLayoutEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.transform = `translate(${item.x}px, ${item.y}px)`;
      containerRef.current.style.width = `${item.w}px`;
    }
  }, [item.x, item.y, item.w]);

  return (
    <div 
      ref={containerRef}
      className={`absolute p-1 group ${dragged ? '' : 'dynamic-block-transition'}`}
    >
      {/* Controles del Bloque */}
      <div className="absolute -top-8 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
         <button 
           onMouseDown={(e: React.MouseEvent) => { e.stopPropagation(); }}
           draggable
           onDragStart={(e: React.DragEvent<HTMLElement>) => onDragStart(e, item.id)}
           className="p-1.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 hover:text-blue-400"
           title="Mover"
         >
           <Move size={14} />
         </button>
         <button 
           onClick={onClone}
           className="p-1.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 hover:text-green-400"
           title="Clonar"
         >
           <Copy size={14} />
         </button>
         <button 
           onClick={onRemove}
           className="p-1.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-400 hover:text-red-400"
           title="Eliminar"
         >
           <Trash2 size={14} />
         </button>
      </div>

      {/* Render del Componente */}
      <div className={`transition-transform ${dragged ? 'scale-105 opacity-50' : 'scale-100'}`}>
         <Component metadata={block.metadata} />
      </div>
    </div>
  );
};
