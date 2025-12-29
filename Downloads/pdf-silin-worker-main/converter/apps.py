"""Converter app."""

# Django
from django.apps import AppConfig


class ConverterAppConfig(AppConfig):
    """Converted App Config."""
    name = "converter"

    def ready(self):
        from converter.workers.sqs import SQSWORKER
        SQSWORKER.setup()
        SQSWORKER.start()
