FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY deploy/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY taskflow_core ./taskflow_core
COPY service_api ./service_api
COPY scripts ./scripts
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "service_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
