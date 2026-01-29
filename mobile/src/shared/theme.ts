/**
 * GoDrive Design System Tokens
 */

export const colors = {
    // Brand Colors
    primary: {
        50: '#eef4ff',
        100: '#dbe7fe',
        200: '#bfd4fe',
        300: '#93b8fd',
        400: '#6092fa',
        500: '#135bec', // Primary Brand Color
        600: '#0d4fd4',
        700: '#0a3fb0',
        800: '#0d3690',
        900: '#103175',
        950: '#0c1f48',
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

    // Semantic Colors
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
    info: {
        500: '#3b82f6',
        600: '#2563eb',
    },

    // Neutral Colors (Backgrounds, Surfaces, Borders)
    neutral: {
        50: '#f9fafb',
        100: '#f3f4f6',
        200: '#e5e7eb',
        300: '#d1d5db',
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
        700: '#374151',
        800: '#1f2937',
        900: '#111827',
        950: '#030712',
    },

    // Abstracted Semantic Aliases
    background: {
        light: '#f6f6f8',
        dark: '#101622',
    },
    surface: {
        light: '#ffffff',
        dark: '#1a212f',
    },
    text: {
        primary: '#111318',
        secondary: '#616f89',
        inverse: '#ffffff',
    },
    border: {
        light: '#dbdfe6',
        dark: '#374151',
    },
} as const;

export const spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    '2xl': 48,
    '3xl': 64,
} as const;

export const radius = {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
} as const;

export const typography = {
    fontFamily: {
        sans: 'Inter_400Regular',
        medium: 'Inter_500Medium',
        semibold: 'Inter_600SemiBold',
        bold: 'Inter_700Bold',
    },
    sizes: {
        xs: 12,
        sm: 14,
        base: 16,
        lg: 18,
        xl: 20,
        '2xl': 24,
        '3xl': 30,
        '4xl': 36,
    },
} as const;

export const item = {
    colors,
    spacing,
    radius,
    typography
}
