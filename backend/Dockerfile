FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps for psycopg, build tools for native extensions.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt

COPY . .

# Static collection runs at deploy time on DO App Platform via the
# release process; we still try here so local images are usable too.
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "offside_crm.wsgi", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--preload", \
     "--log-file", "-"]
