import { spawn } from 'node:child_process';
import http from 'node:http';
import https from 'node:https';

const timeoutMs = Number(process.env.VGREPORT_E2E_TIMEOUT_MS ?? '60000');
const devUrl = process.env.VGREPORT_DEV_URL ?? 'http://localhost:1420';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function isReachable(urlString) {
  let url;
  try {
    url = new URL(urlString);
  } catch {
    return false;
  }

  const lib = url.protocol === 'https:' ? https : http;
  return await new Promise((resolve) => {
    const req = lib.request(
      {
        method: 'GET',
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        timeout: 3000,
      },
      (res) => {
        res.resume();
        // Any HTTP response means the dev server is up.
        resolve(true);
      }
    );
    req.on('timeout', () => {
      req.destroy(new Error('timeout'));
    });
    req.on('error', () => resolve(false));
    req.end();
  });
}

async function killTree(pid) {
  if (!pid) return;

  if (process.platform === 'win32') {
    // /T terminates the whole process tree.
    const killer = spawn('taskkill', ['/PID', String(pid), '/T', '/F'], { stdio: 'ignore' });
    await new Promise((resolve) => killer.on('close', resolve));
    return;
  }

  try {
    process.kill(pid, 'SIGTERM');
  } catch {
    // ignore
  }
}

function npmCmd() {
  return process.platform === 'win32' ? 'npm.cmd' : 'npm';
}

async function main() {
  console.log(`[e2e:tauri] Starting tauri dev (timeout=${timeoutMs}ms, url=${devUrl})`);

  const child = spawn(npmCmd(), ['run', 'tauri', 'dev'], {
    stdio: 'inherit',
    cwd: process.cwd(),
    windowsHide: true,
  });

  let exited = false;
  let exitCode = null;

  child.on('exit', (code) => {
    exited = true;
    exitCode = code;
  });

  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (exited) {
      throw new Error(`tauri dev exited early with code ${exitCode}`);
    }

    // eslint-disable-next-line no-await-in-loop
    const ok = await isReachable(devUrl);
    if (ok) {
      console.log('[e2e:tauri] Dev URL reachable; smoke OK.');
      await killTree(child.pid);
      return;
    }

    // eslint-disable-next-line no-await-in-loop
    await sleep(500);
  }

  await killTree(child.pid);
  throw new Error(`Timed out waiting for dev URL: ${devUrl}`);
}

main().catch((err) => {
  console.error(`[e2e:tauri] FAIL: ${err?.message ?? String(err)}`);
  process.exitCode = 1;
});
