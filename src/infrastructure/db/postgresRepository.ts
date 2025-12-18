import { Pool } from 'pg';

export default class PostgresRepository {
  private pool: Pool;

  constructor() {
    console.log('[DB] Initializing Postgres connection');
    console.log('[DB] Host:', process.env.DB_HOST);
    console.log('[DB] Port:', process.env.DB_PORT);
    console.log('[DB] Database:', process.env.DB_NAME);
    console.log('[DB] User:', process.env.DB_USER);
    console.log('[DB] SSL:', process.env.DB_SSL);

    if (!process.env.DB_HOST) {
      throw new Error('DB_HOST env variable is missing');
    }

    this.pool = new Pool({
      host: process.env.DB_HOST,
      port: Number(process.env.DB_PORT || 5432),
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      ssl:
        process.env.DB_SSL === 'true'
          ? { rejectUnauthorized: false }
          : undefined,
      connectionTimeoutMillis: 5000,
    });

    // 🔥 Escuchar errores del pool
    this.pool.on('error', (err) => {
      console.error('[DB] Unexpected pool error', err);
    });
  }

  async getCount(tableName: string): Promise<number> {
    console.log('[DB] Executing getCount on table:', tableName);

    const result = await this.pool.query(
      `SELECT COUNT(*) FROM ${tableName}`
    );

    console.log('[DB] Query result:', result.rows);

    return Number(result.rows[0].count);
  }
}
