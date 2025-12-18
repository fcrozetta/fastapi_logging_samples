import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

try:
    # Only needed when exporting; safe to import conditionally
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except Exception:  # pragma: no cover
    OTLPSpanExporter = None  # type: ignore

def init(app: FastAPI):
    service_name = os.getenv("OTEL_SERVICE_NAME", "fastapi-logging-samples")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    enable_tracing = os.getenv("OTEL_TRACING_ENABLED", "true").lower() in {"1", "true", "yes", "on"}

    # Always install a real provider (so span context is valid and IDs are not 0)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    trace.set_tracer_provider(provider)

    # Enable log correlation (requires OTEL_PYTHON_LOG_CORRELATION=true to inject)
    LoggingInstrumentor().instrument(set_logging_format=True)

    # Create server spans for requests
    FastAPIInstrumentor().instrument_app(app,excluded_urls="metrics,healthcheck,healthz")

    # Export only if configured (AKS)
    if enable_tracing and otlp_endpoint:
        if OTLPSpanExporter is None:
            raise RuntimeError("OTLP exporter not available; install opentelemetry-exporter-otlp")

        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
