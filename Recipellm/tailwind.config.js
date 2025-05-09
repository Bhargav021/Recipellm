/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        secondary: {
          50: '#f6fee7',
          100: '#ecfcce',
          200: '#daf8a2',
          300: '#c2f067',
          400: '#a9e336',
          500: '#8bc915',
          600: '#6da00c',
          700: '#517a0e',
          800: '#426213',
          900: '#395215',
        },
        accent: {
          50: '#fff4ed',
          100: '#ffe6d4',
          200: '#ffc9a8',
          300: '#ffa570',
          400: '#ff7838',
          500: '#ff5911',
          600: '#ff3d09',
          700: '#cc2a00',
          800: '#a12405',
          900: '#82220a',
        },
        bright: {
          50: '#fdfdfd',
          100: '#fcfcfc',
          200: '#fafafa',
          300: '#f8f8f8',
          400: '#f3f3f3',
          500: '#eeeeee',
          600: '#e2e2e2',
          700: '#d6d6d6',
          800: '#b0b0b0',
          900: '#878787',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        charcoal: {
          700: '#303030',
          750: '#282828',
          800: '#212121',
          850: '#1a1a1a',
          900: '#121212',
          950: '#0a0a0a',
        },
        white: '#ffffff',
        black: '#000000',
        greenTheme: {
          cream: '#FAF3E0',
          deepGreen: '#2E5339',
          mutedOlive: '#556B5D',
          softGreen: '#D7E8D0',
          darkForest: '#1E392A',
          lightCream: '#FFF9F2',
          hoverGreen: '#BFD8B8',
        }
      }
    },
  },
  plugins: [
    function({ addVariant }) {
      addVariant('theme-green', '.theme-green &');
    }
  ]
} 