FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --create-home app \
    && mkdir -p /data \
    && chown app:app /data

COPY api/requirements.txt api/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r api/requirements.txt

COPY --chown=app:app api api
COPY --chown=app:app scripts scripts

USER app

EXPOSE 8000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
