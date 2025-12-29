from rest_framework import status
from rest_framework.exceptions import APIException

from constants import (
    DocumentApiErrorStr, PDFConverterManagerErrorStr, TemplateManagerErrorStr,
    ClientCredentialsFlowErrorStr
)


class DocumentApiError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = DocumentApiErrorStr
    default_code = DocumentApiErrorStr


class ClientCredentialsFlowError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = ClientCredentialsFlowErrorStr
    default_code = ClientCredentialsFlowErrorStr


class PDFConverterManagerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = PDFConverterManagerErrorStr
    default_code = PDFConverterManagerErrorStr


class TemplateManagerError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = TemplateManagerErrorStr
    default_code = TemplateManagerErrorStr
