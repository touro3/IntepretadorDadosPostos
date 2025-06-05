FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock* /app/

ENV UV_SYSTEM_PYTHON=1

RUN uv sync --no-dev

COPY . /app

EXPOSE 11000

CMD ["uv", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:11000", "--workers", "2"]