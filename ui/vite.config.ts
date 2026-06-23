import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import path from "path"

const sdkRoot = path.resolve(__dirname, "node_modules/@openai/apps-sdk-ui/dist/es")

export default defineConfig({
  plugins: [tailwindcss(), react()],
  resolve: {
    alias: {
      "@openai/apps-sdk-ui/components/Badge": path.join(sdkRoot, "components/Badge/index.js"),
      "@openai/apps-sdk-ui/components/Button": path.join(sdkRoot, "components/Button/index.js"),
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
  },
})
