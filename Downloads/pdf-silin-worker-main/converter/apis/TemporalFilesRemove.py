from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.conf import settings

from constants import temporal as temporalStr, temporalFilesRemovedStr


class TemporalFilesRemoveApi(APIView):
    authentication_classes = []

    def get(self, request):
        from shutil import rmtree

        try:
            rmtree(f"{settings.DOWNLOAD_FOLDER}{temporalStr}")
        except Exception:
            pass
        return Response(temporalFilesRemovedStr, status=status.HTTP_200_OK)
