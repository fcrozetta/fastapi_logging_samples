# Logging samples

> This is a wip.

This api contain multiple endpoints that send different log messages, using different log levels, and some endpoints that cause an exception to be thrown. 

## Quick Start

`docker run -p 80:80 ghcr.io/fcrozetta/fastapi_logging_samples`

## Env vars

`LOG_FORMAT`: change the default logger format: the default format is: " %(name)s :: %(levelname)s :: %(message)s"
