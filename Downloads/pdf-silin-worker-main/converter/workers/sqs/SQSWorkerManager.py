import logging
import multiprocessing
import json
from time import time
from threading import Thread
from uuid import uuid1

from rest_framework import serializers

from constants import (
    EmptyStringDiff,
    StringValue, BinaryValue,
    loggerConfig, S3Folder,
    SQSWorkerName, responseMetadata, httpStatusCode,
    messagesStr, attributesStr, templateName,
    content, contextStr, receiptHandleStr, MessageattributesStr,
    bodyStr, bodyUppercaseStr, templateStr,
    UTF8, subFolderStr,
    traceParentStr, registerDocumentStr, sendSNSStr,
    taxDocumentTypeId as taxDocumentTypeIdStr, NameStr,
    relatedSourceId, messageIdStr, processedStr,
    destinationsStr
)
from converter.repositories.aws.SQSManager import SQSManager
from converter.repositories.RedisManager import RedisManager
from converter.services.PDFConverterManager import PDFConverterManager
from converter.serializers import inline_serializer

logging.basicConfig(format=loggerConfig)


class SQSWorkerManager(multiprocessing.Process):
    def __init__(
        self,
        sqsManager: SQSManager,
        redisManager: RedisManager,
        pdfConverterManager: PDFConverterManager,
        bucketName: str,
        s3Subfolder: str = S3Folder,
        converterQueueName: str = EmptyStringDiff,
        maxNumberOfMessages: int = 10,
        maxWaitTimeSeconds: int = 20,
        visibilityTimeout: int = 30,
        cacheTimeout: int = 60,
        processNumber: int = 1,
        name: str = SQSWorkerName,
        daemon: bool = True,
    ):
        self.sqsManager = sqsManager
        self.redisManager = redisManager
        self.pdfConverterManager = pdfConverterManager
        self.bucketName = bucketName
        self.s3Subfolder = s3Subfolder
        self.converterQueueName = converterQueueName
        self.maxNumberOfMessages = maxNumberOfMessages
        self.maxWaitTimeSeconds = maxWaitTimeSeconds
        self.waitTimeSeconds = maxWaitTimeSeconds
        self.visibilityTimeout = visibilityTimeout
        self.cacheTimeout = cacheTimeout
        self.processNumber = processNumber
        multiprocessing.Process.__init__(self, name=name, daemon=daemon)

    def setup(self):
        cpuCount = multiprocessing.cpu_count()
        if 2 < cpuCount and cpuCount <= self.processNumber:
            self.processNumber = cpuCount
        logging.log(
            logging.ERROR,
            f"Setup: SQSWorkerManager with {self.processNumber} process",
        )
        self.semaphore = multiprocessing.Semaphore(self.processNumber)

    def run(self):
        self.initTime = time()
        while True:
            try:
                response = self.sqsManager.receiveSqsMessage(
                    self.converterQueueName,
                    maxNumberOfMessages=self.maxNumberOfMessages,
                    visibilityTimeout=self.visibilityTimeout,
                    waitTimeSeconds=self.waitTimeSeconds,
                )
                if (
                    response.get(responseMetadata, {}).get(httpStatusCode, False)
                    == 200
                    and messagesStr in response.keys()
                ):
                    self.waitTimeSeconds = 1
                    receivedMessages = response.get(messagesStr, [])
                    for aMessage in receivedMessages:
                        if self._canAcquireCacheLock(aMessage):
                            self.semaphore.acquire()
                            aProcess = Thread(
                                target=self._processMessage,
                                args=(self.semaphore, aMessage,),
                            )
                            aProcess.start()
                    continue
                self.waitTimeSeconds = int(self.maxWaitTimeSeconds)
                self.initTime = self.pdfConverterManager.cleanDownloadFolder(self.initTime)
            except Exception as exc:
                self.waitTimeSeconds = int(self.maxWaitTimeSeconds)
                import traceback
                logging.log(
                    logging.ERROR,
                    f"SQSWorkerManager.run: {traceback.format_exc()}. {str(exc)}",
                )

    def _processMessage(self, semaphore, message={}):
        try:
            messageContent = self._getMessageContent(message)
            ownFileName = messageContent.get(bodyStr, str(uuid1()))

            self.pdfConverterManager.process(
                messageContent[attributesStr][templateName],
                contents=[
                    {
                        NameStr: ownFileName,
                        relatedSourceId: (
                            str(messageContent.get(attributesStr).get(relatedSourceId))
                            if messageContent.get(attributesStr, {}).get(
                                relatedSourceId, None
                            ) is not None
                            else None
                        ),
                        content: messageContent[attributesStr][contextStr]
                    }
                ],
                s3Folder=messageContent.get(attributesStr, {}).get(
                    subFolderStr, self.s3Subfolder
                ),
                registerDocument=messageContent.get(attributesStr, {}).get(
                    registerDocumentStr, True
                ),
                sendSNS=messageContent.get(attributesStr, {}).get(
                    sendSNSStr, True
                ),
                tax_document_type_id=(
                    int(messageContent.get(attributesStr).get(taxDocumentTypeIdStr))
                    if messageContent.get(attributesStr, {}).get(
                        taxDocumentTypeIdStr, None
                    ) is not None
                    else None
                ),
                destinations=messageContent.get(attributesStr, {}).get(
                    destinationsStr, None
                ),
            )

            self.sqsManager.deleteSqsMessage(
                self.converterQueueName, message.get(receiptHandleStr, EmptyStringDiff)
            )
        except Exception as exc:
            self._deleteCacheLock(message)
            import traceback
            logging.log(
                logging.ERROR,
                f"SQSWorkerManager._processMessage: {traceback.format_exc()}. {str(exc)}",
            )
            raise exc
        finally:
            semaphore.release()

    class MessageSerializer(serializers.Serializer):
        body = serializers.CharField(required=False)
        attributes = inline_serializer(many=False, fields={
            templateName: serializers.CharField(),
            taxDocumentTypeIdStr: serializers.IntegerField(required=False),
            contextStr: serializers.DictField(),
            subFolderStr: serializers.CharField(required=False),
            registerDocumentStr: serializers.BooleanField(default=True, required=False),
            relatedSourceId: serializers.UUIDField(required=False),
            sendSNSStr: serializers.BooleanField(default=True, required=False),
            destinationsStr: serializers.ListField(child=serializers.CharField(), required=False)
        })

    def _getMessageContent(self, message={}) -> dict:
        messageAttributes = message.get(MessageattributesStr, {})

        messageContent = {}
        messageContent[attributesStr] = {}

        if message.get(bodyUppercaseStr, None) is not None:
            messageContent[bodyStr] = message[bodyUppercaseStr]

        if messageAttributes.get(templateStr, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][templateName] = messageAttributes[templateStr][StringValue]

        if messageAttributes.get(taxDocumentTypeIdStr, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][taxDocumentTypeIdStr] = messageAttributes[taxDocumentTypeIdStr][StringValue]

        if messageAttributes.get(contextStr, {}).get(BinaryValue, None) is not None:
            messageContent[attributesStr][contextStr] = json.loads(
                messageAttributes[contextStr][BinaryValue]
                .decode(UTF8)
            )

        if messageAttributes.get(subFolderStr, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][subFolderStr] = messageAttributes[subFolderStr][StringValue]

        if messageAttributes.get(relatedSourceId, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][relatedSourceId] = messageAttributes[relatedSourceId][StringValue]

        if messageAttributes.get(destinationsStr, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][destinationsStr] = messageAttributes[destinationsStr][StringValue].split(",")

        messageContent[attributesStr][registerDocumentStr] = messageAttributes.get(
            registerDocumentStr, {}).get(StringValue, True)
        messageContent[attributesStr][sendSNSStr] = messageAttributes.get(sendSNSStr, {}).get(StringValue, True)

        if messageAttributes.get(traceParentStr, {}).get(StringValue, None) is not None:
            messageContent[attributesStr][traceParentStr] = messageAttributes[traceParentStr][StringValue]

        serializer = self.MessageSerializer(data=messageContent)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    def _canAcquireCacheLock(self, message: dict = {}) -> bool:
        redisClient = self.redisManager.getClient()
        messageId = message.get(messageIdStr, EmptyStringDiff)
        return redisClient.set(messageId, processedStr, self.cacheTimeout, nx=True)

    def _deleteCacheLock(self, message: dict = {}):
        redisClient = self.redisManager.getClient()
        messageId = message.get(messageIdStr, EmptyStringDiff)
        redisClient.delete(messageId)
