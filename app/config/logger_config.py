'''
Configuration for logger(s)
'''
import logging
import os

def init_logger():
    # create auxiliary variables
    # loggerName = Path(__file__).stem

    # create logging formatter
    fmt = os.getenv("LOG_FORMAT", " %(name)s :: %(levelname)s :: %(message)s")
    logFormatter = logging.Formatter(fmt=fmt)

    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logFormatter)

    # Add console handler to logger
    logger.addHandler(consoleHandler)
    logger.debug("Logger initialized")