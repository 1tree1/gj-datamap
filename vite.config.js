import { defineConfig } from "vite";
// GitHub Pages: https://1tree1.github.io/gj-datamap/
export default defineConfig({
  base: process.env.GH_PAGES ? "/gj-datamap/" : "/",
  build: { target: "es2022" },   // top-level await (config.js 동적 import)
});
