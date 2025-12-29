from rest_framework.views import APIView
from rest_framework import status, serializers, exceptions
from rest_framework.response import Response

from json import loads

from django.conf import settings

from converter.repositories.aws.S3Manager import S3Manager
from converter.services.PDFConverterManager import PDFConverterManager
from converter.serializers import inline_serializer

from constants import (
    EmptyString, EmptyStringDiff, templateStr,
    contentsStr, Id as IdStr, pdfToBase64 as pdfToBase64Str,
    filesStr, content as contentStr, NameStr
)


class FileConvertApi(APIView):
    authentication_classes = []

    class InputSerializer(serializers.Serializer):
        contents = inline_serializer(many=True, fields={
            NameStr: serializers.CharField(required=False),
            contentStr: serializers.DictField()
        })
        template = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        files = inline_serializer(many=True, fields={
            IdStr: serializers.CharField(),
            pdfToBase64Str: serializers.CharField()
        })

    def post(self, request):
        s3Manager = S3Manager(settings.AWS_REGION, settings.AWS_ACCESS_KEY, settings.AWS_SECRET_ACCESS)
        pdfConverterManager = PDFConverterManager(
            s3Manager,
            settings.S3_BUCKET, settings.DOWNLOAD_FOLDER, settings.CONVERTED_FOLDER, settings.BARCODES_FOLDER
        )

        requestData = request.data.dict()
        try:
            requestData[contentsStr] = requestData.get(contentsStr, None)
            requestData[contentsStr] = loads(requestData[contentsStr]) if requestData[contentsStr] is not None else None
        except Exception as e:
            raise exceptions.ValidationError(f"invalid field contents: {e}")

        serializer_input = self.InputSerializer(data=requestData)
        serializer_input.is_valid(raise_exception=True)
        requestData = serializer_input.validated_data

        results = pdfConverterManager.process(
            templateName=requestData.get(templateStr, EmptyStringDiff),
            contents=requestData.get(contentsStr, []),
            uploadS3=False,
            convertBase64=True,
            registerDocument=False,
            sendSNS=False
        )

        response = []
        [
            response.append({
                IdStr: result.get(IdStr, EmptyString),
                pdfToBase64Str: result.get(pdfToBase64Str, EmptyString),
            })
            for result in results
        ]

        serializer_output = self.OutputSerializer({filesStr: response})

        return Response(serializer_output.data, status=status.HTTP_200_OK)
