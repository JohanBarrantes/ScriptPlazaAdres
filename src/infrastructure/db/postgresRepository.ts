import { Pool } from 'pg'; 

class PostgresRepository {
  private pool: Pool;

  constructor() {
 
    this.pool = new Pool({
      host: 'localhost', 
      port: 5432,
      user: 'your-username',
      password: 'your-password',
      database: 'your-database',
    });
  }


  async getCount(tableName: string): Promise<number> {
    const query = `SELECT COUNT(*) FROM ${tableName}`;
    const result = await this.pool.query(query);
    return parseInt(result.rows[0].count, 10);
  }
}

export default PostgresRepository;
