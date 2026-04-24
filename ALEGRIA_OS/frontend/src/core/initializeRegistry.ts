import { registry } from './UIRegistry';
import ProvidersBlock from '../blocks/ProvidersBlock';
import RadarBlock from '../blocks/RadarBlock';
import AnimaStatusBlock from '../blocks/AnimaStatusBlock';

/**
 * Inicializa el registro de bloques del sistema.
 */
export const initializeRegistry = () => {
  // Registrar bloque de Proveedores
  registry.register({
    id: 'providers_manager',
    name: 'Gestor de APIs',
    capability: 'config',
    component: ProvidersBlock,
    metadata: { version: '2.0.0' }
  });

  // Registrar otros bloques existentes
  registry.register({
    id: 'radar_scan',
    name: 'Radar Scan',
    capability: 'research',
    component: RadarBlock
  });

  registry.register({
    id: 'anima_status',
    name: 'Estado de Anima',
    capability: 'system',
    component: AnimaStatusBlock
  });
  
  console.log('🛡️ [REGISTRY] Bloques del sistema inicializados.');
};
