/// <reference types="vitest" />
import { defineConfig, Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

/*
 * locuszoom 0.11 and its bundled d3 v3 read the global object through a
 * top level `this`, which is window under webpack's non-strict CommonJS but
 * undefined once Vite turns them into strict ES modules.
 */
const legacyGlobalThis: { file: RegExp, replace: [RegExp, string][] }[] = [
  // d3 v3 is one big `!function() { ... }();`, run it with window as this
  { file: /locuszoom\/node_modules\/d3\/d3\.js$/, replace: [[/\}\(\);\s*$/, '}.call(window);']] },
  {
    file: /locuszoom\/dist\/locuszoom\.app\.min\.js$/,
    replace: [
      // the UMD wrapper passes this as the global object
      [/\}\(this,function\(t\)\{/, '}(window,function(t){'],
      // and the factory captures it again for the bundled plugins
      [/e=this,a=function\(g\)\{/, 'e=window,a=function(g){'],
    ],
  },
]

const patch = (id: string, code: string): string | null => {
  const fix = legacyGlobalThis.find(({ file }) => file.test(id))
  if (!fix) return null
  return fix.replace.reduce((patched, [from, to]) => {
    if (!from.test(patched)) throw new Error(`legacy-global-this: ${from} not found in ${id}`)
    return patched.replace(from, to)
  }, code)
}

// production build: rollup transform
const legacyGlobalThisPlugin = (): Plugin => ({
  name: 'legacy-global-this',
  enforce: 'pre',
  transform: (code, id) => patch(id, code),
})

export default defineConfig({
  plugins: [react(), legacyGlobalThisPlugin()],
  // dev server: dependencies are pre-bundled by esbuild, outside the rollup pipeline
  optimizeDeps: {
    esbuildOptions: {
      plugins: [{
        name: 'legacy-global-this',
        setup(build) {
          build.onLoad({ filter: /(locuszoom\.app\.min|d3)\.js$/ }, ({ path }) => {
            const code = patch(path, fs.readFileSync(path, 'utf8'))
            return code === null ? undefined : { contents: code, loader: 'js' }
          })
        },
      }],
    },
  },
  server: { port: 3000 },
  // the build is copied into pheweb/serve/static by the build script
  build: { outDir: 'build' },
  test: {
    globals: true,
    environment: 'jsdom',
    css: false,
    setupFiles: ['src/setupTests.ts'],
    // keep the `Object {` style of the existing jest snapshots
    snapshotFormat: { printBasicPrototype: true },
  },
})
