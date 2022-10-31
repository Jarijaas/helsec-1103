import { resolve } from 'path'
import { mergeWindicssConfig, defineConfig } from 'vite-plugin-windicss'
import BaseConfig from '@slidev/client/windi.config'

// extend the base config
export default mergeWindicssConfig(
  BaseConfig,
  defineConfig({
    extract: {
      include: [
        resolve(__dirname, '**/*.{vue,ts}'),
      ],
    },
    shortcuts: {
      // custom the default background
      'bg-main': 'bg-purple-50 text-[#f43f5e] dark:(bg-purple-50 text-[#f43f5e])',
      'border-image': 'border border-[#121212] border-opacity-10 shadow-md shadow-[#121212] dark:(border-red-100 border-opacity-10 shadow-red-100)',
      'bg-barBottom': 'bg-red-500 text-red-50 dark:(bg-red-900 text-red-50)',
    },
    theme: {
      extend: {
        // fonts can be replaced here, remember to update the web font links in `index.html`
        fontFamily: {
          sans: '"Rubik", ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"',
          mono: '"Fira Code", monospace',
        }
      },
    },
  }),
)
