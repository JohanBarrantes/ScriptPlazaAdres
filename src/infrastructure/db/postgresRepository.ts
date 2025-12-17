const pool = require('../../config/dbConfig');

class PostgresRepository {
  async getCount(tableName) {
    const query = `SELECT COUNT(*) FROM ${tableName}`;
    const result = await pool.query(query);
    return parseInt(result.rows[0].count, 10);
  }
}

module.exports = PostgresRepository;
