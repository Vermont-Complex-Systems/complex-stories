// src/lib/utils/duckdb.js - Shared Instance Approach
import * as duckdb from '@duckdb/duckdb-wasm';
import duckdb_wasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url';
import duckdb_wasm_next from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url';

let db = null;
let conn = null;
let isInitialized = false;

async function initDuckDB() {
  if (isInitialized) return;

  const MANUAL_BUNDLES = {
    mvp: {
      mainModule: duckdb_wasm,
      mainWorker: new URL('@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js', import.meta.url).href,
    },
    eh: {
      mainModule: duckdb_wasm_next,
      mainWorker: new URL('@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js', import.meta.url).href,
    },
  };

  const bundle = await duckdb.selectBundle(MANUAL_BUNDLES);
  const worker = new Worker(bundle.mainWorker);
  const logger = new duckdb.ConsoleLogger();

  db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle.mainModule);
  conn = await db.connect();
  isInitialized = true;
}

export async function registerParquetFile(url, tableName) {
  await initDuckDB();
  
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
  
  const buffer = await response.arrayBuffer();
  await db.registerFileBuffer(`${tableName}.parquet`, new Uint8Array(buffer));
  
  await conn.query(`CREATE VIEW '${tableName}' AS SELECT * FROM parquet_scan('${tableName}.parquet')`);
}

export async function query(sql) {
  await initDuckDB();
  const result = await conn.query(sql);
  
  return result.toArray().map(row => {
    const obj = Object.fromEntries(row);
    
    // Convert BigInt to numbers
    Object.keys(obj).forEach(key => {
      if (typeof obj[key] === 'bigint') {
        obj[key] = Number(obj[key]);
      }
    });
    
    return obj;
  });
}