import logging

from django.shortcuts import render

log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
logger = logging.getLogger(__name__)
logger.level = logging.INFO
handler = logging.FileHandler(
    '/home/peka97/verbalvoyager/Verbal-Voyager/verbalvoyager/logs/debug.log')
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)
