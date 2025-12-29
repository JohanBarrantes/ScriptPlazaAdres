import boto3
import logging

from rest_framework import exceptions

from constants import (
    S3GetClientError, S3GetResourceError, loggerConfig
)

logging.basicConfig(format=loggerConfig)


class S3Manager:
    client = None
    resource = None

    def __init__(
        self,
        regionName=None,
        accessKeyId=None,
        secretAccessKey=None
    ):
        self.client = None
        self.resource = None
        self.regionName = regionName
        self.accessKeyId = accessKeyId
        self.secretAccessKey = secretAccessKey

    def getClient(self):
        if self.client is None:
            try:
                self.client = boto3.client(
                    "s3",
                    region_name=self.regionName,
                    aws_access_key_id=self.accessKeyId,
                    aws_secret_access_key=self.secretAccessKey,
                )
            except Exception as e:
                logging.log(
                    logging.ERROR, S3GetClientError
                )
                raise exceptions.APIException(f"{S3GetClientError}: {e}")
        return self.client

    def getResource(self):
        if self.resource is None:
            try:
                self.resource = boto3.resource(
                    "s3",
                    region_name=self.regionName,
                    aws_access_key_id=self.accessKeyId,
                    aws_secret_access_key=self.secretAccessKey,
                )
            except Exception as e:
                logging.log(
                    logging.ERROR, S3GetResourceError
                )
                raise exceptions.APIException(f"{S3GetResourceError}: {e}")
        return self.resource

    def downloadS3File(self, bucketName, filePathName, destinationFile):
        resource = self.getResource()
        try:
            bucketResource = resource.Bucket(bucketName)
            with open(destinationFile, "wb") as file:
                bucketResource.download_fileobj(filePathName, file)
        except Exception as e:
            logging.log(
                logging.ERROR,
                f"S3Manager.downloadS3File: Could not get {filePathName} from {bucketName}",
            )
            raise exceptions.NotFound(
                f"S3Manager.downloadS3File: Could not get {filePathName} from {bucketName}: {e}"
            )

    def uploadS3File(self, filePathName, bucketName, destinationFile):
        resource = self.getResource()
        try:
            bucketResource = resource.Bucket(bucketName)
            with open(filePathName, "rb") as file:
                bucketResource.upload_fileobj(file, destinationFile)
        except Exception as e:
            raise exceptions.APIException(
                detail=f"S3Manager.uploadS3File: Could not upload {filePathName}: {e}"
            )

    def deleteS3File(self, bucketName, filePathName):
        client = self.getClient()
        try:
            client.delete_object(Bucket=bucketName, Key=filePathName)
        except Exception as e:
            raise exceptions.APIException(f"S3Manager.deleteS3File could not delete {filePathName}: {e}")
