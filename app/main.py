from fastapi import FastAPI
from prometheus_client import make_asgi_app
from config.logger_config import init_logger

from routers.sampling_logs import app as logRouter
from routers.sampling_errors import app as errorRouter

app = FastAPI(debug=True)
init_logger()



# Prometheus config
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(logRouter)
app.include_router(errorRouter)
