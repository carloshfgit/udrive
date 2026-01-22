module.exports = {
    root: true,
    extends: [
        'expo',
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
        'plugin:react-hooks/recommended',
    ],
    plugins: [
        '@typescript-eslint',
        'react',
        'react-hooks',
    ],
    parser: '@typescript-eslint/parser',
    parserOptions: {
        ecmaFeatures: {
            jsx: true,
        },
        ecmaVersion: 'latest',
        sourceType: 'module',
    },
    settings: {
        react: {
            version: 'detect',
        },
    },
    rules: {
        // TypeScript
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
        '@typescript-eslint/no-explicit-any': 'warn',

        // React
        'react/react-in-jsx-scope': 'off',
        'react/prop-types': 'off',

        // React Hooks
        'react-hooks/rules-of-hooks': 'error',
        'react-hooks/exhaustive-deps': 'warn',

        // Geral
        'no-console': ['warn', { allow: ['warn', 'error'] }],
        'prefer-const': 'error',
    },
    ignorePatterns: [
        'node_modules/',
        '.expo/',
        'dist/',
        'web-build/',
    ],
};
