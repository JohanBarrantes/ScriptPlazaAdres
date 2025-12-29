import boto3
import logging

from rest_framework import exceptions

from constants import (
    SQSGetClientError, QueueUrl, SQSSendMessageInvalidContent,
    SQSSendMessageUnsupportedOperation, SQSReceiveMessageOverLimit,
    SQSDeleteMessageInvalidFormat, SQSDeleteMessageInvalidReceiptHandle,
    loggerConfig
)

logging.basicConfig(format=loggerConfig)


class SQSManager:
    client = None

    def __init__(
        self,
        regionName=None,
        accessKeyId=None,
        secretAccessKey=None
    ):
        self.client = None
        self.regionName = regionName
        self.accessKeyId = accessKeyId
        self.secretAccessKey = secretAccessKey

    def getClient(self):
        if self.client is None:
            try:
                self.client = boto3.client(
                    "sqs",
                    region_name=self.regionName,
                    aws_access_key_id=self.accessKeyId,
                    aws_secret_access_key=self.secretAccessKey,
                )
            except Exception as e:
                logging.log(
                    logging.ERROR, SQSGetClientError
                )
                raise exceptions.APIException(f"{SQSGetClientError}: {e}")
        return self.client

    def getQueueUrl(self, queueName):
        client = self.getClient()
        try:
            return client.get_queue_url(QueueName=queueName)[QueueUrl]
        except Exception as e:
            logging.log(
                logging.ERROR,
                f"SQSManager.getQueueUrl: Queue {queueName} doesn't exist",
            )
            raise exceptions.APIException(f"SQSManager.getQueueUrl: Queue {queueName} doesn't exist: {e}")

    def sendSqsMessage(
        self, queueName, messageBody, messageAttributes={}, delaySeconds=0
    ):
        client = self.getClient()
        try:
            queueUrl = self.getQueueUrl(queueName)
            return client.send_message(
                QueueUrl=queueUrl,
                MessageBody=messageBody,
                DelaySeconds=delaySeconds,
                MessageAttributes=messageAttributes,
            )
        except client.exceptions.InvalidMessageContents:
            logging.log(
                logging.ERROR, SQSSendMessageInvalidContent
            )
            raise exceptions.APIException(SQSSendMessageInvalidContent)
        except client.exceptions.UnsupportedOperation:
            logging.log(
                logging.ERROR, SQSSendMessageUnsupportedOperation
            )
            raise exceptions.APIException(SQSSendMessageUnsupportedOperation)

    def receiveSqsMessage(
        self,
        queueName,
        messageAttributes=["All"],
        maxNumberOfMessages=1,
        visibilityTimeout=10,
        waitTimeSeconds=0,
    ):
        client = self.getClient()
        try:
            queueUrl = self.getQueueUrl(queueName)
            return client.receive_message(
                QueueUrl=queueUrl,
                MessageAttributeNames=messageAttributes,
                MaxNumberOfMessages=maxNumberOfMessages,
                VisibilityTimeout=visibilityTimeout,
                WaitTimeSeconds=waitTimeSeconds,
            )
        except client.exceptions.OverLimit:
            logging.log(logging.ERROR, SQSReceiveMessageOverLimit)
            raise exceptions.APIException(SQSReceiveMessageOverLimit)

    def deleteSqsMessage(self, queueName, receiptHandle):
        client = self.getClient()
        try:
            queueUrl = self.getQueueUrl(queueName)
            return client.delete_message(
                QueueUrl=queueUrl, ReceiptHandle=receiptHandle
            )
        except client.exceptions.InvalidIdFormat:
            logging.log(logging.ERROR, SQSDeleteMessageInvalidFormat)
            raise exceptions.APIException(SQSDeleteMessageInvalidFormat)
        except client.exceptions.ReceiptHandleIsInvalid:
            logging.log(
                logging.ERROR, SQSDeleteMessageInvalidReceiptHandle
            )
            raise exceptions.APIException(SQSDeleteMessageInvalidReceiptHandle)
