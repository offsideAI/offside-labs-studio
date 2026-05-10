/** @type {import("prettier").Config} */
module.exports = {
  semi: true,
  singleQuote: false,
  trailingComma: "all",
  printWidth: 100,
  tabWidth: 2,
  bracketSameLine: false,
  arrowParens: "always",
  plugins: ["prettier-plugin-tailwindcss"],
};
