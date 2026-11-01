import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

// 단일 HTML 출력: JS·CSS·JSON 전부 인라인. file:// 더블클릭으로 열려야 한다.
export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    target: 'es2022',
    cssCodeSplit: false,
    assetsInlineLimit: 100000000,
    chunkSizeWarningLimit: 5000,
  },
});
