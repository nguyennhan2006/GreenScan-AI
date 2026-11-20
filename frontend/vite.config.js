import { existsSync, readdirSync, unlinkSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

/**
 * Every build starts with an empty <outDir>/assets. Without this the bundles of earlier builds pile up
 * (141 files in dist/assets on 18/11/2026) and travel into the submission zip and the public demo.
 *
 * Vite's own `emptyOutDir` relies on fs.rmSync, which on Windows with Node 24 silently does nothing when
 * the path holds non-ASCII characters (this project sits under a folder with Vietnamese diacritics).
 * Removing the files one by one with unlinkSync works on every path.
 */
function emptyAssets() {
  let assets
  return {
    name: 'gs-empty-assets',
    apply: 'build',
    configResolved(config) { assets = resolve(config.root, config.build.outDir, 'assets') },
    buildStart() {
      if (!existsSync(assets)) return
      for (const name of readdirSync(assets)) unlinkSync(join(assets, name))
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [emptyAssets(), react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
