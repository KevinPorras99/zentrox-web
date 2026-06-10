import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  // Ruta base para GitHub Pages: https://<usuario>.github.io/zentrox-web/
  base: command === 'build' ? '/zentrox-web/' : '/',
  plugins: [react(), tailwindcss()],
}))
