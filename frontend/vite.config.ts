import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Where the FastAPI backend runs (override with API_PROXY_TARGET=http://host:port npm run dev)
const apiTarget = process.env.API_PROXY_TARGET ?? 'http://127.0.0.1:3000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Forward /api/* to the FastAPI backend, so the browser sees one origin (no CORS setup needed)
    proxy: {
      '/api': apiTarget,
    },
  },
})
