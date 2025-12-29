
from converter.workers.sqs.SQSWorkerManager import SQSWorkerManager

from converter.services.PDFConverterManager import PDFConverterManager

from converter.repositories.DocumentApiManager import DocumentApiManager
from converter.repositories.ClientCredentialsFlowManager import ClientCredentialsFlowManager
from converter.repositories.RedisManager import RedisManager
from converter.repositories.aws.SQSManager import SQSManager
from converter.repositories.aws.S3Manager import S3Manager
from django.conf import settings


# Dependency Injection and starting worker
sqsManager = SQSManager(
    settings.AWS_REGION,
    settings.AWS_ACCESS_KEY,
    settings.AWS_SECRET_ACCESS
)
s3Manager = S3Manager(
    settings.AWS_REGION,
    settings.AWS_ACCESS_KEY,
    settings.AWS_SECRET_ACCESS
)
redisManager = RedisManager(settings.REDIS_HOST, settings.REDIS_PORT)
clientCredentialsApi = ClientCredentialsFlowManager(
    settings.AUTH2_URL,
    settings.APPLICATION_ID,
    settings.APPLICATION_SECRET
)
documentApi = DocumentApiManager(settings.DOCUMENT_MANAGEMENT_URL, clientCredentialsApi)
pdfConverterManager = PDFConverterManager(
    s3Manager,
    settings.S3_BUCKET,
    settings.DOWNLOAD_FOLDER,
    settings.CONVERTED_FOLDER,
    settings.BARCODES_FOLDER,
    documentApi
)
SQSWORKER = SQSWorkerManager(
    sqsManager,
    redisManager,
    pdfConverterManager,
    settings.S3_BUCKET,
    settings.S3_SUBFOLDER,
    settings.AWS_GENERATOR_QUEUE,
    settings.MAX_NUMBER_OF_MESSAGES,
    settings.TIME_POLLING,
    settings.VISIBILITY_TIMEOUT,
    settings.CACHE_TIMEOUT,
    settings.NUMBER_OF_PROCESSES,
    name='Queue-Main-Process'
)
