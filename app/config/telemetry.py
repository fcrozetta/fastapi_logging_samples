import os, logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
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


def _attach_root_handlers(logger_name: str) -> None:
    log = logging.getLogger(logger_name)
    # log.handlers = logging.getLogger().handlers  # reuse root handlers/formatters
    log.propagate = False  # avoid double logging


def init(app: FastAPI):
    service_name = os.getenv("OTEL_SERVICE_NAME", "fastapi-logging-samples")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    enable_tracing = os.getenv("OTEL_TRACING_ENABLED", "true").lower() in {"1", "true", "yes", "on"}

    # Always install a real provider (so span context is valid and IDs are not 0)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    trace.set_tracer_provider(provider)

    # Enable log correlation (requires OTEL_PYTHON_LOG_CORRELATION=true to inject)
    LoggingInstrumentor().instrument(set_logging_format=True)
    _attach_root_handlers("uvicorn")
    _attach_root_handlers("uvicorn.error")
    _attach_root_handlers("uvicorn.access")


    # Create server spans for requests
    FastAPIInstrumentor().instrument_app(app,excluded_urls="metrics,healthcheck,healthz")

    # Export only if configured (AKS)
    if enable_tracing and otlp_endpoint:
        if OTLPSpanExporter is None:
            raise RuntimeError("OTLP exporter not available; install opentelemetry-exporter-otlp")

        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))


