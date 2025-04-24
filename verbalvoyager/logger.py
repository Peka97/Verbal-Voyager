import logging

from django.conf import settings



def get_logger(level=logging.ERROR):
    logger = logging.getLogger()
    logger.setLevel(level)
    log_format = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

    if level == logging.DEBUG:
        handler = logging.FileHandler(settings.CURRENT_CONFIG.DEBUG_LOG_FILE_PATH)

    else:
        handler = logging.FileHandler(settings.CURRENT_CONFIG.DJANGO_LOG_FILE_PATH)

    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    return logger


def get_words_logger(level=logging.ERROR):
    logger = logging.getLogger('words')
    logger.setLevel(level)
    log_format = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

    handler = logging.FileHandler(settings.CURRENT_CONFIG.WORDS_LOG_FILE_PATH)

    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    return logger
