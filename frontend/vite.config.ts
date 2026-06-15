import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// base: "./" 로 상대경로 빌드 → pywebview가 file://로 로드 가능
export default defineConfig({
  plugins: [react()],
  base: "./",
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
