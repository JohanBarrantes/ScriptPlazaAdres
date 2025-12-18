import { Pool } from 'pg';

class PostgresRepository {
  private pool: Pool;

  constructor() {
    this.pool = new Pool({
      host: process.env.DB_HOST!,
      port: Number(process.env.DB_PORT || 5432),
      user: process.env.DB_USER!,
      password: process.env.DB_PASSWORD!,
      database: process.env.DB_NAME!,
      ssl: process.env.DB_SSL === 'true'
        ? { rejectUnauthorized: false }
        : false
    });
  }

  async getCount(tableName: string): Promise<number> {
    const query = `SELECT COUNT(*) FROM ${tableName}`;
    const result = await this.pool.query(query);
    return Number(result.rows[0].count);
  }
}

export default PostgresRepository;
