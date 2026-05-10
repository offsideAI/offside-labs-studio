#!/usr/bin/env node
/**
 * OpenAPI codegen.
 *
 * Fetches the Django OpenAPI schema (drf-spectacular) and generates:
 *   - TypeScript client at packages/api-client/src/generated/schema.ts
 *   - Swift client mirror under frontend-ios/Generated/ (wired in M6)
 *
 * Source URL defaults to http://localhost:8000/api/schema/ — override with
 * OPENAPI_URL. Run `pnpm backend:up` first so the Django dev server is reachable.
 */

import { execSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "../..");
const tsOut = resolve(repoRoot, "packages/api-client/src/generated/schema.ts");
const swiftOutDir = resolve(repoRoot, "frontend-ios/Generated");

const url = process.env.OPENAPI_URL ?? "http://localhost:8000/api/schema/";

console.log(`[codegen] source: ${url}`);

mkdirSync(dirname(tsOut), { recursive: true });
mkdirSync(swiftOutDir, { recursive: true });

// --- TypeScript client (openapi-typescript) ---

try {
  console.log("[codegen] generating TS client via openapi-typescript …");
  execSync(`pnpm exec openapi-typescript "${url}" --output "${tsOut}"`, {
    stdio: "inherit",
    cwd: repoRoot,
  });
  console.log(`[codegen] wrote ${tsOut}`);
} catch (err) {
  console.error(`[codegen] TS codegen failed: ${err instanceof Error ? err.message : err}`);
  console.error("[codegen] Is the Django dev server running? Try: pnpm backend:up");
  process.exit(1);
}

// --- Swift client (placeholder until M6 wires the real generator) ---

const swiftPlaceholder = resolve(swiftOutDir, ".gitkeep");
writeFileSync(
  swiftPlaceholder,
  `# Swift OpenAPI client lands here.\n` +
    `# Real codegen is wired in M6 (iOS shell + auth + read-only views).\n` +
    `# Source: ${url}\n` +
    `# Generated at: ${new Date().toISOString()}\n`,
);
console.log(`[codegen] Swift output dir ready: ${swiftOutDir} (real generator lands in M6)`);

console.log("[codegen] done.");
