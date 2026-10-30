import { defineConfig } from 'vite';
export default defineConfig({esbuild:{jsx:"automatic"},server:{proxy:{'/api':{target:'http://127.0.0.1:8000',rewrite:p=>p.replace(/^\/api/,'')}}}});
