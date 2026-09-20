import { defineConfig } from "vite";
import { resolve } from "path";
// GitHub Pages: https://1tree1.github.io/gj-datamap/
export default defineConfig({
  base: process.env.GH_PAGES ? "/gj-datamap/" : "/",
  build: { target: "es2022", rollupOptions: { input: { main: resolve(__dirname, "index.html"), report: resolve(__dirname, "report.html") } } },   // top-level await (config.js 동적 import) · 2페이지
});
