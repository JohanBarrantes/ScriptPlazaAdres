"""Converted URLs."""

# Django
from django.urls import path

from converter.apis.FileConvert import FileConvertApi
from converter.apis.FileConvertAndSave import FileConvertAndSaveApi
from converter.apis.TemporalFilesRemove import TemporalFilesRemoveApi


urlpatterns = [
    path("convert/", FileConvertApi.as_view()),
    path("convert_and_save/", FileConvertAndSaveApi.as_view()),
    path("remove_temporal_files/", TemporalFilesRemoveApi.as_view())
]
