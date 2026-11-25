import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // Loads .env, .env.local, .env.[mode], etc. from the current directory
  // Pass '' as the 3rd argument to load all env vars, or 'VITE_' to load only prefixed ones
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      host: env.VITE_HOST || '127.0.0.1',
      port: Number(env.VITE_PORT) || 5173,
    },
  }
})