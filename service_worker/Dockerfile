FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY deploy/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY taskflow_core ./taskflow_core
COPY service_worker ./service_worker

CMD ["python", "-m", "service_worker.worker"]
