import logging
import logging.handlers

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)

logging.basicConfig(level=logging.INFO)

def get_logger(name: str):
    logger = logging.getLogger(name)

    return logger
