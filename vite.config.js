import { defineConfig } from "vite";
// GitHub Pages: https://1tree1.github.io/gj-datamap/
export default defineConfig({ base: process.env.GH_PAGES ? "/gj-datamap/" : "/" });
