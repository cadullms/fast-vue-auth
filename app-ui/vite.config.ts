import process from 'node:process'
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 5173,
    host: '127.0.0.1', // for port forwarding to work in devcontainer
    proxy: {
      '/api': {
        // Set env var VITE_DEV_PROXY_URL to http://app-api:8000 when running in devcontainer.
        // See run-dev.sh and run-dev-without-container.sh scripts
        target: process.env.VITE_DEV_PROXY_URL ? process.env.VITE_DEV_PROXY_URL : 'http://localhost:8000', 
        changeOrigin: true, // Ensure the request appears to come from the frontend server
        // rewrite: (path) => path.replace(/^\/api/, ''), // Optional: Remove '/api' prefix
      },
    },
  },
})
