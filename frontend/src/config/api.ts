// API Configuration for different environments

// Check if we should use Pyodide (browser-based Python) or backend API
const USE_PYODIDE = import.meta.env.VITE_USE_PYODIDE !== 'false'; // Default to true
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let pyodideWorker: Worker | null = null;

/**
 * Initialize Pyodide worker for browser-based SQL analysis
 */
export function initializePyodideWorker(): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      pyodideWorker = new Worker(new URL('../workers/pyodide.worker.ts', import.meta.url), {
        type: 'module'
      });
      
      pyodideWorker.onmessage = (event) => {
        if (event.data.type === 'ready') {
          console.log('Pyodide worker ready');
          resolve();
        }
      };
      
      pyodideWorker.onerror = (error) => {
        console.error('Worker error:', error);
        reject(error);
      };
      
      pyodideWorker.postMessage({ type: 'init' });
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Parse SQL using Pyodide worker (browser-based)
 */
export function parseSqlWithPyodide(sql: string, dialect?: string): Promise<any> {
  return new Promise((resolve, reject) => {
    if (!pyodideWorker) {
      reject(new Error('Pyodide worker not initialized'));
      return;
    }
    
    const handler = (event: MessageEvent) => {
      pyodideWorker!.removeEventListener('message', handler);
      
      if (event.data.type === 'error') {
        reject(new Error(event.data.error));
      } else if (event.data.type === 'success') {
        resolve(event.data.data);
      }
    };
    
    pyodideWorker.addEventListener('message', handler);
    pyodideWorker.postMessage({
      type: 'parse',
      data: { sql, dialect: dialect || null }
    });
  });
}

/**
 * Parse SQL using backend API
 */
export async function parseSqlWithBackend(sql: string, dialect?: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/parse`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sql,
      dialect: dialect || null
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  baseURL: API_BASE_URL,
  usePyodide: USE_PYODIDE,
  
  /**
   * Main parse function - uses Pyodide if available, falls back to backend
   */
  async parseSql(sql: string, dialect?: string) {
    if (USE_PYODIDE && pyodideWorker) {
      return parseSqlWithPyodide(sql, dialect);
    }
    return parseSqlWithBackend(sql, dialect);
  },
  
  // Direct methods for explicit choice
  parseSqlWithPyodide,
  parseSqlWithBackend,
};

export default api;
