import { Command, Child } from '@tauri-apps/plugin-shell';
import { v4 as uuidv4 } from 'uuid';

interface JsonRpcRequest {
  id: string;
  method: string;
  params: Record<string, any>;
}

interface JsonRpcResponse {
  id: string;
  result?: any;
  error?: any;
}

class SidecarClient {
  private child: Child | null = null;
  private pendingRequests = new Map<string, { resolve: (val: any) => void; reject: (err: any) => void }>();
  private isInitializing = false;
  private isReady = false;
  private logHandlers: ((msg: string) => void)[] = [];

  onLog(handler: (msg: string) => void) {
    this.logHandlers.push(handler);
    return () => {
      this.logHandlers = this.logHandlers.filter(h => h !== handler);
    };
  }

  private emitLog(msg: string) {
    this.logHandlers.forEach(h => h(msg));
  }

  async init() {
    if (this.isReady || this.isInitializing) return;
    this.isInitializing = true;

    console.log("Spawning sidecar...");

    try {
      // Recommended: use the bundled sidecar exe in both dev + prod.
      // Optional escape hatch for local debugging: set VITE_USE_PYTHON_SIDECAR=1.
      const usePythonDev = import.meta.env.DEV && import.meta.env.VITE_USE_PYTHON_SIDECAR === '1';

      this.emitLog(`Sidecar mode: ${usePythonDev ? 'python-dev' : 'bundled exe'}`);

      const command = usePythonDev
        ? Command.create(
            'python-dev',
            ['-u', 'C:\\PYTHON APPS\\Edsembli Replica\\sidecar\\main.py'],
            { cwd: 'C:\\PYTHON APPS\\Edsembli Replica' }
          )
        : Command.sidecar('vgreport-engine');

      command.on('close', (data) => {
        const msg = `Sidecar finished with code ${data.code} and signal ${data.signal}`;
        console.log(msg);
        this.emitLog(msg);
        this.isReady = false;
        this.child = null;
      });

      command.on('error', (error) => {
        const msg = `Sidecar error: "${error}"`;
        console.error(msg);
        this.emitLog(msg);
      });

      command.stdout.on('data', (line) => {
        // console.log(`[PY]: ${line}`);
        try {
          const response = JSON.parse(line) as JsonRpcResponse;
          if (response.id && this.pendingRequests.has(response.id)) {
            const { resolve, reject } = this.pendingRequests.get(response.id)!;
            if (response.error) {
              reject(response.error);
            } else {
              // Preferred shape: { id, result, error }
              // Defensive fallback: some builds may emit { id, ...payload } without a `result` wrapper.
              if (typeof response.result !== 'undefined') {
                resolve(response.result);
              } else {
                resolve(response as any);
              }
            }
            this.pendingRequests.delete(response.id);
          }
        } catch (e) {
          console.warn('Failed to parse sidecar output:', line);
          this.emitLog(`[STDOUT (Raw)]: ${line}`);
        }
      });

      command.stderr.on('data', (line) => {
        console.log(`[PY LOG]: ${line}`);
        this.emitLog(`[PY]: ${line}`);
      });

      this.child = await command.spawn();
      this.isReady = true;
      console.log("Sidecar spawned successfully.");
      this.emitLog("Sidecar spawned successfully.");

    } catch (e) {
      console.error("Failed to spawn sidecar:", e);
      throw e;
    } finally {
      this.isInitializing = false;
    }
  }

  async call(method: string, params: Record<string, any> = {}): Promise<any> {
    if (!this.isReady) {
      await this.init();
    }

    if (!this.child) {
      throw new Error("Sidecar not running");
    }

    const id = uuidv4();
    const request: JsonRpcRequest = { id, method, params };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });

      // Write to stdin
      // Note: write() accepts string or Uint8Array.
      // We must append newline as our python script typically reads line-buffered or expects it.
      const msg = JSON.stringify(request) + "\n";
      this.child!.write(msg).catch(err => {
        this.pendingRequests.delete(id);
        reject(err);
      });

      // Timeout
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Timeout waiting for ${method}`));
        }
      }, 5000);
    });
  }
}

export const sidecar = new SidecarClient();
