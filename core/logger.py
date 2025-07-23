import logging
from logging import handlers
import os

class MaxLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno <= self.level


class Logger:
    def __init__(self, name: str, log_dir: str = "logs", level: str = "DEBUG"):
        dict_level = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        if level not in dict_level:
            raise ValueError(f"Log level invalid: {level}")

        self.logger = logging.getLogger(name)
        self.logger.setLevel(dict_level[level])
        log_format = "[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d | %(message)s"

        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"{name}.log")
        error_log_file = os.path.join(log_dir, f"{name}_error.log")

        formatter = logging.Formatter(
            log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        if not self.logger.handlers:
            file_handler = handlers.RotatingFileHandler(
                log_file, encoding="utf-8", mode='a', maxBytes=5 * 1024 * 1024, backupCount=5
            )
            file_handler.setLevel(dict_level['INFO'])
            file_handler.setFormatter(formatter)
            file_handler.addFilter(MaxLevelFilter(dict_level['WARNING']))

            error_handler = handlers.RotatingFileHandler(
                error_log_file, encoding="utf-8", mode='a', maxBytes=5 * 1024 * 1024, backupCount=3
            )
            error_handler.setLevel(dict_level['ERROR'])
            error_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(dict_level['DEBUG'])
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
