/** @type {import('prettier').Config} */
module.exports = {
  // Basic formatting
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  quoteProps: 'as-needed',
  jsxSingleQuote: true,

  // Indentation
  tabWidth: 2,
  useTabs: false,

  // Line wrapping
  printWidth: 80,
  proseWrap: 'preserve',

  // HTML/JSX formatting
  htmlWhitespaceSensitivity: 'css',
  bracketSpacing: true,
  bracketSameLine: false,
  arrowParens: 'avoid',

  // End of line
  endOfLine: 'lf',

  // File specific overrides
  overrides: [
    {
      files: ['*.json', '*.jsonc'],
      options: {
        printWidth: 120,
      },
    },
    {
      files: ['*.md', '*.mdx'],
      options: {
        proseWrap: 'always',
        printWidth: 100,
      },
    },
    {
      files: ['*.yml', '*.yaml'],
      options: {
        tabWidth: 2,
        singleQuote: false,
      },
    },
  ],

  // Plugins
  plugins: [
    'prettier-plugin-tailwindcss', // Must be last
  ],

  // Tailwind CSS plugin options
  tailwindConfig: './tailwind.config.js',
  tailwindFunctions: ['clsx', 'cn', 'cva'],
};