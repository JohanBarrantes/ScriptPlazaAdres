import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import PostgresRepository from '../db/postgresRepository';
import CountService from '../../application/countService';

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const tableName = event.queryStringParameters?.tableName || 'mi_tabla';

  try {
    const repository = new PostgresRepository();
    const service = new CountService(repository);
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
