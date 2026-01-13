/**
 * e2e_tauri_build_check.mjs
 *
 * Verifies that `tauri build` produces expected installer artifacts.
 * This script does NOT run the build (that's slow); it checks that artifacts
 * exist from a prior build. Use it in CI after `npm run build:tauri`.
 *
 * Usage:
 *   node scripts/e2e_tauri_build_check.mjs
 *
 * Env vars:
 *   VGREPORT_BUILD_DIR  - path to release bundle dir (default: src-tauri/target/release/bundle)
 */

import { existsSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';

const bundleDir = process.env.VGREPORT_BUILD_DIR
  ? resolve(process.env.VGREPORT_BUILD_DIR)
  : resolve(process.cwd(), 'src-tauri', 'target', 'release', 'bundle');

const expectedArtifacts = [
  { path: 'msi/vgreport_0.1.0_x64_en-US.msi', minSize: 1_000_000 },
  { path: 'nsis/vgreport_0.1.0_x64-setup.exe', minSize: 1_000_000 },
];

function main() {
  console.log(`[build-check] Bundle dir: ${bundleDir}`);

  if (!existsSync(bundleDir)) {
    throw new Error(`Bundle dir not found: ${bundleDir}. Run 'npm run build:tauri' first.`);
  }

  const results = [];

  for (const artifact of expectedArtifacts) {
    const fullPath = join(bundleDir, artifact.path);
    const exists = existsSync(fullPath);
    let size = 0;

    if (exists) {
      const stat = statSync(fullPath);
      size = stat.size;
    }

    const ok = exists && size >= artifact.minSize;
    results.push({ path: artifact.path, exists, size, minSize: artifact.minSize, ok });

    const status = ok ? '✓' : '✗';
    const sizeStr = exists ? `${(size / 1_000_000).toFixed(2)} MB` : 'N/A';
    console.log(`  ${status} ${artifact.path} (${sizeStr})`);
  }

  const allOk = results.every((r) => r.ok);

  if (!allOk) {
    throw new Error('One or more build artifacts missing or too small.');
  }

  console.log('[build-check] All artifacts OK.');
}

try {
  main();
} catch (err) {
  console.error(`[build-check] FAIL: ${err?.message ?? String(err)}`);
  process.exitCode = 1;
}
