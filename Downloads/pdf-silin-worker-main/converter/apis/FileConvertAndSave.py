from rest_framework.views import APIView
from rest_framework import status, serializers, exceptions
from rest_framework.response import Response

from json import loads

from django.conf import settings

from converter.auth.jwt_validator import AccessJWTValidator
from converter.repositories.aws.S3Manager import S3Manager
from converter.services.PDFConverterManager import PDFConverterManager
from converter.repositories.DocumentApiManager import DocumentApiManager
from converter.serializers import inline_serializer

from constants import (
    EmptyString, EmptyStringDiff, templateStr,
    contentsStr, Id as IdStr, subFolderStr, pathStr,
    filesStr, fileMetadata as fileMetadataStr, S3Destination as S3DestinationStr,
    filenameStr, fileType as fileTypeStr, bucketName as bucketNameStr,
    content as contentStr, registerDocumentStr, sendSNSStr,
    NameStr, taxDocumentTypeId as taxDocumentTypeIdStr,
    relatedSourceId as relatedSourceIdStr, destinationsStr
)


class FileConvertAndSaveApi(APIView):
    authentication_classes = [AccessJWTValidator]

    class InputSerializer(serializers.Serializer):
        contents = inline_serializer(many=True, fields={
            NameStr: serializers.CharField(required=False),
            relatedSourceIdStr: serializers.UUIDField(required=False),
            contentStr: serializers.DictField()
        })
        template = serializers.CharField()
        subfolder = serializers.CharField(default=settings.S3_SUBFOLDER, required=False)
        tax_document_type_id = serializers.IntegerField(required=False)
        register_document = serializers.BooleanField(default=True, required=False)
        send_SNS = serializers.BooleanField(default=True, required=False)
        destinations = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        files = inline_serializer(many=True, fields={
            IdStr: serializers.CharField(),
            fileMetadataStr: inline_serializer(many=False, fields={
                pathStr: serializers.CharField(),
                filenameStr: serializers.CharField(),
                fileTypeStr: serializers.CharField(),
                bucketNameStr: serializers.CharField()
            })
        })

    def post(self, request):
        s3Manager = S3Manager(settings.AWS_REGION, settings.AWS_ACCESS_KEY, settings.AWS_SECRET_ACCESS)
        documentApi = DocumentApiManager(settings.DOCUMENT_MANAGEMENT_URL, None)
        pdfConverterManager = PDFConverterManager(
            s3Manager,
            settings.S3_BUCKET,
            settings.DOWNLOAD_FOLDER,
            settings.CONVERTED_FOLDER,
            settings.BARCODES_FOLDER,
            documentApi
        )

        requestData = request.data.dict()
        try:
            requestData[contentsStr] = (
                loads(requestData[contentsStr])
                if requestData.get(contentsStr, None) is not None
                else None
            )
        except Exception as e:
            raise exceptions.ValidationError(f"invalid field contents: {e}")

        try:
            requestData[destinationsStr] = (
                requestData[destinationsStr].split(",")
                if requestData.get(destinationsStr, None) is not None
                else None
            )
        except Exception as e:
            raise exceptions.ValidationError(f"invalid field destinations: {e}")

        serializer_input = self.InputSerializer(data=requestData)
        serializer_input.is_valid(raise_exception=True)
        requestData = serializer_input.validated_data

        response = []

        results = pdfConverterManager.process(
            templateName=requestData.get(templateStr, EmptyStringDiff),
            contents=requestData.get(contentsStr, []),
            uploadS3=True,
            s3Folder=requestData.get(subFolderStr, settings.S3_SUBFOLDER),
            registerDocument=requestData.get(registerDocumentStr, True),
            sendSNS=requestData.get(sendSNSStr, True),
            tax_document_type_id=requestData.get(taxDocumentTypeIdStr, None),
            destinations=requestData.get(destinationsStr, None),
            token=request.auth.get("token", None)
        )

        [
            response.append({
                IdStr: result.get(IdStr, EmptyString),
                fileMetadataStr: {
                    pathStr: result.get(S3DestinationStr, EmptyString),
                    filenameStr: result.get(NameStr, EmptyString),
                    fileTypeStr: result.get(fileTypeStr, EmptyString),
                    bucketNameStr: result.get(bucketNameStr, EmptyString)
                },
            })
            for result in results
        ]

        serializer_output = self.OutputSerializer({filesStr: response})

        return Response(serializer_output.data, status=status.HTTP_200_OK)
