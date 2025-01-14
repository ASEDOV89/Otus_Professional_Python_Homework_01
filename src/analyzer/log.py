import logging

import structlog


def get_logger(config):
    log_file_path = config.get("LOG_FILE", None)
    logger = structlog.get_logger()

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        logging.getLogger().handlers[0].setFormatter(formatter)

    return logger
