import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import path from "node:path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const buildTarget = env.VITE_BUILD_TARGET ?? "devkit";
  const apiHost = env.VITE_API_HOST ?? "http://localhost:8000";

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["favicon.svg"],
        manifest: {
          name: "FlightImpact",
          short_name: "FlightImpact",
          description: "FlightImpact launch monitor companion app",
          theme_color: "#0e7c5a",
          background_color: "#0a0e14",
          display: "standalone",
          orientation: "portrait",
          icons: [
            { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
            { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
            { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any maskable" },
          ],
        },
      }),
    ],
    resolve: {
      alias: { "@": path.resolve(__dirname, "src") },
    },
    define: {
      __BUILD_TARGET__: JSON.stringify(buildTarget),
    },
    server: {
      host: true,
      port: 5173,
      proxy: {
        "/api": { target: apiHost, changeOrigin: true },
        "/ws": { target: apiHost.replace(/^http/, "ws"), ws: true, changeOrigin: true },
      },
    },
  };
});
