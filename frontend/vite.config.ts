import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Forward /api/* to the FastAPI backend, so the browser sees one origin (no CORS setup needed)
    proxy: {
      '/api': 'http://127.0.0.1:3000',
    },
  },
})
