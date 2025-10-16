# Startup Guide

This guide walks a new contributor through running TaskFlow the first time.

## 1. Prerequisites
- Docker Desktop or Docker Engine 20+
- Docker Compose v2 (`docker compose` CLI)
- Git
- Optional for local-only service work:
  - Python 3.11 + `pip`
  - Node.js 18 LTS + `npm`

## 2. Clone the Repository
```bash
git clone https://github.com/<your-org>/ai-side-project.git
cd ai-side-project
```

## 3. Configure Environment
All runtime variables are in `deploy/env.example`.

```bash
cp deploy/env.example .env
```

The default values match the docker-compose stack (MySQL, Redis, RabbitMQ). Adjust only if you need different ports or credentials.

## 4. Launch the Full Stack
The easiest way to run everything is Docker Compose. It starts:
- MySQL, Redis, RabbitMQ
- Automatic DB migrations
- FastAPI (`service_api`)
- Worker (`service_worker`)
- React frontend

```bash
docker compose --project-directory deploy -f deploy/docker-compose.yml up --build
```

The first run builds images and applies Alembic migrations. When all services are healthy:
- API: http://localhost:8000
- Frontend: http://localhost:5001
- RabbitMQ UI (optional): http://localhost:15672 (guest/guest)

Stop the stack with `Ctrl+C` or `docker compose down`.

## 5. Verify Functionality
1. Open the frontend at http://localhost:5001.
2. Create a task via the form.
3. Watch the task list update and real-time toast notifications when the worker processes the job.

## 6. Development Workflow (Optional)

### Backend (FastAPI)
```bash
pip install -r deploy/requirements.txt
uvicorn service_api.app:app --reload
```
Keep MySQL/Redis/RabbitMQ running via Docker (use `docker compose` but disable the `api` service with `--scale api=0` if needed).

### Worker
```bash
pip install -r deploy/requirements.txt
python -m service_worker.worker
```

### Frontend
```bash
cd frontend
npm install
npm start
```
Set `REACT_APP_API_BASE` / `REACT_APP_WS_URL` in `.env.local` if you override API host/port.

## 7. Useful Commands
- Run only infrastructure (DB/cache/broker): `docker compose --project-directory deploy -f deploy/docker-compose.yml up mysql redis rabbitmq`
- Apply migrations manually: `docker compose --project-directory deploy -f deploy/docker-compose.yml run --rm migrate`
- Tail logs for a service: `docker compose --project-directory deploy -f deploy/docker-compose.yml logs -f api`

## 8. Troubleshooting
- **Migrations fail**: ensure `mysql-data/` volume is writable, then rerun `docker compose ... run --rm migrate`.
- **Ports already in use**: edit `deploy/docker-compose.yml` or `.env` to change exposed ports, then restart.
- **WebSocket disconnects**: confirm Redis is running (`docker compose ps redis`) and restart the API service.
- **Frontend cannot reach API**: check CORS origins in `.env` and confirm `REACT_APP_API_BASE`.

Welcome aboard! Reach out in the project chat if you hit setup issues not covered here.
