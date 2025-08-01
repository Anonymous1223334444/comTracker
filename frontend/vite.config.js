import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path'; // Importez le module path

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['orca-eternal-specially.ngrok-free.app', 'localhost:5173', '127.0.0.1:5005'],
    proxy: {
      '/api/presse':   { target: 'http://localhost:5005', changeOrigin: true, rewrite: p => p.replace(/^\/api\/presse/,   '') },
      '/api/reddit':   { target: 'http://localhost:5003', changeOrigin: true, rewrite: p => p.replace(/^\/api\/reddit/,   '') },
      '/api/rss':      { target: 'http://localhost:5002', changeOrigin: true, rewrite: p => p.replace(/^\/api\/rss/,      '') },
      '/api/twitter':  { target: 'http://localhost:5001', changeOrigin: true, rewrite: p => p.replace(/^\/api\/twitter/,  '') },
      '/api/youtube':  { target: 'http://localhost:5004', changeOrigin: true, rewrite: p => p.replace(/^\/api\/youtube/,  '') },
      '/api/linkedin': { target: 'http://localhost:5006', changeOrigin: true, rewrite: p => p.replace(/^\/api\/linkedin/, '') },
      '/api/ai':       { target: 'http://localhost:5007', changeOrigin: true, rewrite: p => p.replace(/^\/api\/ai/, '') }
    }
  },
  plugins: [react()],
  resolve: {
    alias: {
      // Configurez l'alias pour @/
      "@": path.resolve(__dirname, "./src"),
    },
  },
});