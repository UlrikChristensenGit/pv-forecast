import logging
import os
from logging import StreamHandler

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from opentelemetry import _logs as logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)

exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APP_INSIGHTS_CONNECTION_STRING"]
)

processor = BatchLogRecordProcessor(exporter)

provider = LoggerProvider()
logs.set_logger_provider(provider)

provider.add_log_record_processor(processor)

azure_handler = LoggingHandler()

stream_handler = StreamHandler()


def get_logger(name: str):
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    logger.addHandler(azure_handler)

    return logger
