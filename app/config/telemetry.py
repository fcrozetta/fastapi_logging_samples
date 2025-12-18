import os, logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from pythonjsonlogger.jsonlogger import JsonFormatter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

try:
    # Only needed when exporting; safe to import conditionally
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except Exception:  # pragma: no cover
    OTLPSpanExporter = None  # type: ignore


logger = logging.getLogger("fastapi_logging_samples")

class CorrelatedExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            # This executes while the request span is still current
            logger.exception("Unhandled exception in request")
            raise

def setup_json_logging() -> None:
    level = os.getenv("OTEL_PYTHON_LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT",None)
    handler = logging.StreamHandler()
    if  log_format == "json":
        formatter = JsonFormatter(
            # These fields become JSON keys
            "%(asctime)s %(levelname)s %(name)s %(message)s "
            "%(otelTraceID)s %(otelSpanID)s %(otelServiceName)s",
            rename_fields={
                "asctime": "ts",
                "levelname": "level",
                "name": "logger",
                "message": "msg",
                "otelTraceID": "trace_id",
                "otelSpanID": "span_id",
                "otelServiceName": "service",
            },
        )
        handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # Force uvicorn to use the same handler/formatter (prevents mixed logs)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        log = logging.getLogger(name)
        log.handlers = [handler]
        log.setLevel(level)
        log.propagate = False


def init(app: FastAPI):
    service_name = os.getenv("OTEL_SERVICE_NAME", "fastapi-logging-samples")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    enable_tracing = os.getenv("OTEL_TRACING_ENABLED", "true").lower() in {"1", "true", "yes", "on"}

    # Always install a real provider (so span context is valid and IDs are not 0)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    trace.set_tracer_provider(provider)

    # Enable log correlation (requires OTEL_PYTHON_LOG_CORRELATION=true to inject)
    LoggingInstrumentor().instrument(set_logging_format=False)
    setup_json_logging()


    # Create server spans for requests
    FastAPIInstrumentor().instrument_app(app,excluded_urls="metrics,healthcheck,healthz")

    # Export only if configured (AKS)
    if enable_tracing and otlp_endpoint:
        if OTLPSpanExporter is None:
            raise RuntimeError("OTLP exporter not available; install opentelemetry-exporter-otlp")

        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))


