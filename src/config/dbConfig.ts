import { Pool } from 'pg';

function required(name: string, value?: string) {
  if (!value) {
    throw new Error(`[DB CONFIG] Missing environment variable: ${name}`);
  }
  return value;
}

console.log('[DB CONFIG] Initializing PostgreSQL pool...');
console.log('[DB CONFIG] ENV snapshot:', {
  PG_HOST: process.env.PG_HOST,
  PG_PORT: process.env.PG_PORT,
  PG_DATABASE: process.env.PG_DATABASE,
  PG_USER: process.env.PG_USER,
  PG_SSL: process.env.PG_SSL,
});

const pool = new Pool({
  host: required('PG_HOST', process.env.PG_HOST),
  port: Number(process.env.PG_PORT || 5432),
  database: required('PG_DATABASE', process.env.PG_DATABASE),
  user: required('PG_USER', process.env.PG_USER),
  password: required('PG_PASSWORD', process.env.PG_PASSWORD),
  ssl:
    process.env.PG_SSL === 'true'
      ? { rejectUnauthorized: false }
      : undefined,
  connectionTimeoutMillis: 5000,
  max: 5,
});

pool.on('connect', () => {
  console.log('[DB POOL] New client connected');
});

pool.on('error', (err) => {
  console.error('[DB POOL] Unexpected error', err);
});

(async () => {
  try {
    const client = await pool.connect();
    console.log('[DB POOL] Connection test successful');
    client.release();
  } catch (err) {
    console.error('[DB POOL] Connection test FAILED', err);
  }
})();

export default pool;
