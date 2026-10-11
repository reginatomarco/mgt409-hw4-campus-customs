import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The FastAPI backend runs on port 8000. These paths are forwarded to it.
    proxy: {
      // xfwd adds X-Forwarded-For, so the backend's per-guest chat limit sees each shopper's real IP.
      '/api': { target: 'http://127.0.0.1:8000', xfwd: true },
      '/images': 'http://127.0.0.1:8000',
    },
  },
})
