import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import tailwindcss from '@tailwindcss/vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? '/SistemaLEC/' : '/',
  plugins: [vue(), tailwindcss()],
  build: {
    outDir: process.env.GITHUB_PAGES === 'true'
      ? path.resolve(__dirname, '../dist')
      : path.resolve(__dirname, '../src/static/dist'),
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  }
})
