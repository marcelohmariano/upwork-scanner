import logging
import sys


def get_logger(level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger('upwork-scanner')
    logger.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    return logger
