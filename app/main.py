from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pathlib import Path
import logging
import os

app = FastAPI(debug=True)

# create auxiliary variables
loggerName = Path(__file__).stem

# create logging formatter
fmt = os.getenv("LOG_FORMAT", " %(name)s :: %(levelname)s :: %(message)s")
logFormatter = logging.Formatter(fmt=fmt)

# create logger
logger = logging.getLogger(loggerName)
logger.setLevel(logging.DEBUG)

# create console handler
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)

# Add console handler to logger
logger.addHandler(consoleHandler)


# Prometheus config
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/debug")
def send_debug(message: str = "Debug message"):
    """send a debug message"""
    logger.debug(message)


@app.get("/info", tags=["logs"])
def send_info(message: str = "info message"):
    logger.info("Sample of info")


@app.get("/exception", tags=["logs"])
def send_exception(message: str = "exception message"):
    logger.exception(message)


@app.get("/exception_stack", tags=["logs"])
def send_exception_details(message: str = "exception_details message"):
    logger.exception(
        message,
        exc_info=Exception({"message": "information inside the exception"}),
    )


@app.get("/error", tags=["logs"])
def send_error(message: str = "error message"):
    logger.error(message)


@app.get("/critical", tags=["logs"])
def send_critical(message: str = "critical message"):
    logger.critical(message)


@app.get("/stacktrace", tags=["errors"])
def broke_code():
    # * this code should create an error
    x = 1 / 0
    return x
