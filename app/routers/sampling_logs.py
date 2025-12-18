'''routes that will log sample logging messages, for debug, info, exception and critical_error'''
from fastapi.routing import APIRouter
from logging import getLogger

app = APIRouter(prefix='/logging', tags=['logs'])
logger = getLogger()

@app.get("/debug")
def send_debug(message: str = "Debug message"):
    """send a debug message"""
    logger.debug(message)


@app.get("/info")
def send_info(message: str = "info message"):
    logger.info("Sample of info")


@app.get("/exception")
def send_exception(message: str = "exception message"):
    logger.exception(message)


@app.get("/exception_stack")
def send_exception_details(message: str = "exception_details message"):
    logger.exception(
        message,
        exc_info=Exception({"message": "information inside the exception"}),
    )


@app.get("/error")
def send_error(message: str = "error message"):
    logger.error(message)


@app.get("/critical")
def send_critical(message: str = "critical message"):
    logger.critical(message)