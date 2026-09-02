import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  { ignores: ["dist", "coverage", "src/api/schema.d.ts", "playwright-report", "test-results"] },
  js.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    extends: [...tseslint.configs.strictTypeChecked, ...tseslint.configs.stylisticTypeChecked],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: { "react-hooks": reactHooks, "react-refresh": reactRefresh },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-unnecessary-condition": "off",
    },
  },
  {
    files: ["e2e/**"],
    languageOptions: { globals: globals.node },
    rules: {
      "@typescript-eslint/no-non-null-assertion": "off",
      "@typescript-eslint/no-invalid-void-type": "off", // Playwright fixture convention
    },
  },
  {
    files: ["**/*.test.{ts,tsx}", "src/test/**"],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      "@typescript-eslint/no-non-null-assertion": "off",
      "@typescript-eslint/unbound-method": "off",
    },
  },
  { files: ["**/*.js"], languageOptions: { globals: globals.node } },
  prettier,
);
