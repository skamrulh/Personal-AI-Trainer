import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// FIX 9: Proxy /api and /health to the Flask backend during local development.
// This removes the need to set VITE_BACKEND_URL manually and avoids CORS issues.
// In production (Docker), nginx in the frontend container handles the proxying.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
