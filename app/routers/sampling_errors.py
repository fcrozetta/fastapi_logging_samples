'''routes that will log sample logging messages, for debug, info, exception and critical_error'''
from fastapi.routing import APIRouter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from logging import getLogger

app = APIRouter(prefix='/errors', tags=['errors'])
logger = getLogger()

@app.get("/stacktrace")
def broke_code():
    # * this code should create an error
    x = 1 / 0
    return x