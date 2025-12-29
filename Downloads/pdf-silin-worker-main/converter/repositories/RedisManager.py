import logging
from redis import Redis
from rest_framework import exceptions

from constants import RedisGetClientError, loggerConfig

logging.basicConfig(format=loggerConfig)


class RedisManager:
    host = None
    port = None
    client = None

    def __init__(
        self,
        host=None,
        port=None,
    ):
        self.host = host
        self.port = port
        self.client = None

    def getClient(self):
        if self.client is None:
            try:
                self.client = Redis(host=self.host, port=self.port)
            except Exception as e:
                logging.log(
                    logging.ERROR,
                    RedisGetClientError,
                )
                raise exceptions.APIException(f"{RedisGetClientError}: {e}")
        return self.client
