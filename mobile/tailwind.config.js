/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./App.{js,jsx,ts,tsx}",
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    presets: [require("nativewind/preset")],
    theme: {
        extend: {
            colors: {
                // Cores principais do GoDrive (baseado no design #135bec)
                primary: {
                    50: '#eef4ff',
                    100: '#dbe7fe',
                    200: '#bfd4fe',
                    300: '#93b8fd',
                    400: '#6092fa',
                    500: '#135bec',
                    600: '#0d4fd4',
                    700: '#0a3fb0',
                    800: '#0d3690',
                    900: '#103175',
                    950: '#0c1f48',
                },
                // Cores de fundo
                background: {
                    light: '#f6f6f8',
                    dark: '#101622',
                },
                // Cores de superfície
                surface: {
                    light: '#ffffff',
                    dark: '#1a212f',
                },
                // Cores de texto
                text: {
                    primary: '#111318',
                    secondary: '#616f89',
                },
                // Cores de borda
                border: {
                    light: '#dbdfe6',
                    dark: '#374151',
                },
                secondary: {
                    50: '#fdf4ff',
                    100: '#fae8ff',
                    200: '#f5d0fe',
                    300: '#f0abfc',
                    400: '#e879f9',
                    500: '#d946ef',
                    600: '#c026d3',
                    700: '#a21caf',
                    800: '#86198f',
                    900: '#701a75',
                    950: '#4a044e',
                },
                success: {
                    500: '#22c55e',
                    600: '#16a34a',
                },
                warning: {
                    500: '#f59e0b',
                    600: '#d97706',
                },
                error: {
                    500: '#ef4444',
                    600: '#dc2626',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
};
