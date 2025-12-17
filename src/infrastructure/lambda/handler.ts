import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda'; // Importa los tipos de Lambda
const PostgresRepository = require('../db/postgresRepository');
const CountService = require('../../application/countService');

const repository = new PostgresRepository();
const service = new CountService(repository);

exports.handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const tableName = event.queryStringParameters?.tableName || 'mi_tabla'; // Asegúrate de usar queryStringParameters si es de API Gateway
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
