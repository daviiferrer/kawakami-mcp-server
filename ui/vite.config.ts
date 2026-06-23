import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [tailwindcss(), react()],
  build: {
    // O resource MCP é embutido em um único HTML; dividir chunks criaria URLs externas.
    chunkSizeWarningLimit: 600,
  },
})
