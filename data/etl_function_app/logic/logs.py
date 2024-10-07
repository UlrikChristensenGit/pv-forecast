import logging
import logging.handlers

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)

def get_logger(name: str):
    sys_log_handler = logging.handlers.SysLogHandler(address="/dev/log")

    logger = logging.getLogger(name)
    logger.addHandler(sys_log_handler)

    return logger