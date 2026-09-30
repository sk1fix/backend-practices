import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const API_TARGET = 'http://localhost:8000';

/**
 * Базовый путь сборки. По умолчанию корень домена.
 * Для отдачи из подкаталога: VITE_BASE_PATH=/cloud-storage/ npm run build
 */
const rawBase = process.env.VITE_BASE_PATH ?? '/';
const basePath = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
const apiPrefix = `${basePath.replace(/\/+$/, '')}/api`;

const apiProxy = {
  [apiPrefix]: {
    target: API_TARGET,
    changeOrigin: true,
    // В dev-сервере префикс базового пути снимается, как это делает nginx
    rewrite: (path: string) => path.replace(new RegExp(`^${apiPrefix}`), '/api'),
  },
};

export default defineConfig({
  base: basePath,
  plugins: [react()],
  server: {
    port: 5173,
    proxy: apiProxy,
  },
  preview: {
    port: 4173,
    proxy: apiProxy,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
