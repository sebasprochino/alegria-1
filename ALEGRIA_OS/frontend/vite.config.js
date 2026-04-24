import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    basicSsl()
  ],
  server: {
    https: true,
    host: true,
    proxy: {
      '/api/developer': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/anima': { target: 'http://127.0.0.1:8000', secure: false },
      '/nexus': { target: 'http://127.0.0.1:8000', secure: false },
      '/providers': { target: 'http://127.0.0.1:8000', secure: false },
      '/radar': { target: 'http://127.0.0.1:8000', secure: false },
      '/storage': { target: 'http://127.0.0.1:8000', secure: false },
      '/developer': { target: 'http://127.0.0.1:8000', secure: false },
      '/brand': { target: 'http://127.0.0.1:8000', secure: false },
      '/veoscope': { target: 'http://127.0.0.1:8000', secure: false },
      '/connectors': { target: 'http://127.0.0.1:8000', secure: false },
      '/noticias': { target: 'http://127.0.0.1:8000', secure: false },
      '/motion': { target: 'http://127.0.0.1:8000', secure: false }

    }
  },
  build: {
    rollupOptions: {
      output: {
        // Split vendor libs so they are cached independently and not
        // re-downloaded with every app change.
        manualChunks(id) {
          // Core React runtime — downloaded once, cached forever
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/')) {
            return 'vendor-react';
          }
          // Lucide icons get their own chunk so they don't inflate the app entry
          if (id.includes('node_modules/lucide-react')) {
            return 'vendor-lucide';
          }
          // Remaining node_modules go into a shared vendor chunk
          if (id.includes('node_modules/')) {
            return 'vendor-misc';
          }
        }
      }
    }
  }
})
