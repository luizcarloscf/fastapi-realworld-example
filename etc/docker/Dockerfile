FROM python:3.14-slim

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	POETRY_NO_INTERACTION=1 \
	POETRY_VIRTUALENVS_CREATE=0 \
	POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock README.md ./
COPY conduit ./conduit

RUN python3 -m pip install poetry && \
    python3 -m poetry install

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/python"]

CMD ["-m", "uvicorn", "conduit.main:app", "--host", "0.0.0.0", "--port", "8000"]
