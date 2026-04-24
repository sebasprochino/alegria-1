/**
 * UIRegistry: El motor de composición de UI en tiempo real de ALEGR-IA.
 * Permite registrar capacidades, clonar bloques y gestionar el renderizado dinámico.
 */

export interface UIBlock {
  id: string;
  name: string;
  capability: string;
  component: React.ComponentType<any>;
  metadata?: any;
}

class UIRegistry {
  private blocks: Map<string, UIBlock> = new Map();
  private listeners: Set<() => void> = new Set();

  register(block: UIBlock) {
    this.blocks.set(block.id, block);
    this.notify();
  }

  unregister(id: string) {
    this.blocks.delete(id);
    this.notify();
  }

  getBlocksByCapability(capability: string): UIBlock[] {
    return Array.from(this.blocks.values()).filter(b => b.capability === capability);
  }

  getAllBlocks(): UIBlock[] {
    return Array.from(this.blocks.values());
  }

  /**
   * Clona un bloque existente con un nuevo ID.
   * Esto permite "Versionado Visual" e iteración sin riesgo.
   */
  clone(id: string, newId?: string): UIBlock | null {
    const original = this.blocks.get(id);
    if (!original) return null;

    const clone: UIBlock = {
      ...original,
      id: newId || `${id}_clone_${Math.random().toString(36).substr(2, 9)}`,
      name: `${original.name} (Clone)`,
    };

    this.register(clone);
    return clone;
  }

  subscribe(listener: () => void) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    this.listeners.forEach(l => l());
  }
}

export const registry = new UIRegistry();
export default registry;
