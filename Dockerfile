FROM python:alpine
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1
ENV UV_NO_SYNC=True

WORKDIR /app/
COPY pyproject.toml .
RUN UV_NO_SYNC=False uv sync --no-dev

COPY ./static_site_generator/ ./static_site_generator/
ENTRYPOINT [ "uv", "run", "static_site_generator" ]
