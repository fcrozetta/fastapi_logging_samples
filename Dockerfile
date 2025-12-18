FROM python:3.12-slim

ENV OTEL_EXPORTER_OTLP_ENDPOINT=true
ENV OTEL_PYTHON_LOG_LEVEL=INFO
ENV OTEL_EXPORTER_OTLP_ENDPOINT=""
ENV LOG_FORMAT=json

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]