const PostgresRepository = require('../db/postgresRepository');
const CountService = require('../../application/countService');

const repository = new PostgresRepository();
const service = new CountService(repository);

exports.handler = async (event) => {
  const tableName = event.tableName || 'mi_tabla'; // o del query params
  try {
    const count = await service.execute(tableName);
    return {
      statusCode: 200,
      body: JSON.stringify({ count }),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Error al obtener el count' }),
    };
  }
};
