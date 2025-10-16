# 🧩 TaskFlow – AI-assisted Event-Driven Backend (Multi-Service Architecture)

## Overview
**TaskFlow** is a one-day proof-of-concept demonstrating how AI-assisted development (ChatGPT + GitHub Copilot) can drastically accelerate backend delivery.

The project implements a **microservice-based, event-driven architecture**:
- A **FastAPI async REST API** for task creation, retrieval, and WebSocket status updates
- A **Worker Service** consuming tasks from **RabbitMQ**
- **MySQL** as the single source of truth for task states
- **Redis Pub/Sub + WebSocket** for real-time client notifications
- A **React** dashboard for visualising tasks, creating new work, and receiving live updates

> The system mimics a real-world asynchronous processing pipeline commonly used in AI workflow orchestration (like PEGAAi / MLOps task scheduling).

---

## System Architecture
```
    ┌─────────────────────────────┐
    │        API Service          │
    │  FastAPI (async)            │
    │  1-1 POST /tasks            │
    │  1-2 GET  /tasks/{id}       │
    │  1-3 WS  /ws (Redis PubSub) │
    └───────┬────────────────────┬┘
            │                    │
 Publish MQ │                    │ Subscribe Redis
            │                    │
     ┌──────▼───────────────┐    │
     │        RabbitMQ      │    │
     │   Exchange: task.*   │    │
     └───────────┬──────────┘    │
                 │               │
          ┌──────▼───────────┐   │
          │      Worker      │   │
          │  Consume MQ      │   │
          │  Process task    │   │
          │  Update MySQL    │   │
          │  Publish Redis   │   │
          └─────────┬────────┘   │
                    │            │
            ┌───────▼──────────┐ │
            │      Redis       │<┘
            │   Pub/Sub        │
            └─────────┬────────┘
                      │
              ┌───────▼──────────┐
              │     MySQL        │
              │  tasks (status)  │
              └──────────────────┘
```
---

## Services

### 🧠 API Service (FastAPI)
- **1-1 POST `/tasks`**
  - Validate payload
  - Insert task row into MySQL (`status = PENDING`)
  - Publish `task.created` event to RabbitMQ
  - Return `{ task_id }`
- **1-2 GET `/tasks/{id}`**
  - Query MySQL for task status
- **1-3 WebSocket `/ws`**
  - Open broadcast stream for all task status changes via Redis Pub/Sub (`task.status`)
  - Push real-time status updates when Worker publishes events

---

### ⚙️ Worker Service
- Subscribes to `task.created` queue from RabbitMQ
- For each message:
  1. Mark the task `PROCESSING` in MySQL and broadcast the update
  2. Inspect payload → if it contains a `message` field mark the task `DONE`, otherwise `FAILED`
  3. Handle unexpected errors by flagging the task `FAILED`
  4. Publish final status to the Redis broadcast channel (`task.status`)
- Supports retries, backoff, and idempotency check

### 🖥️ Frontend (React)
- Presents task list, detail view, and creation form
- Opens a WebSocket connection to stream status changes in real time
- Targets the API via `REACT_APP_API_BASE` and `REACT_APP_WS_URL` environment variables

---

## Message & Data Contracts

### 📨 RabbitMQ Message
**Exchange**: `task.topic`
**Routing key**: `task.created`

```json
{
  "task_id": "uuid",
  "payload": { "message": "Task complete" },
  "requested_at": "2025-10-13T02:30:00Z"
}
```
> The worker expects incoming payloads to include a `message` field; if it is missing the task is marked `FAILED`.
---
### 📡 Redis Pub/Sub
**Channel:** `task.status`
**Message Example:**
```json
{
  "task_id": "uuid",
  "status": "PENDING|PROCESSING|DONE|FAILED",
  "updated_at": "2025-10-13T02:31:00Z",
  "message": "Task complete"
}
```
---
### 🗃️ MySQL Schema
```sql

CREATE TABLE tasks (
  id           CHAR(36) PRIMARY KEY,
  title        VARCHAR(255) NOT NULL,
  payload      JSON NULL,
  status       ENUM('PENDING','PROCESSING','DONE','FAILED') NOT NULL,
  created_at   DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at   DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                ON UPDATE CURRENT_TIMESTAMP(6),
  finished_at  DATETIME(6) NULL
);

CREATE INDEX idx_tasks_status ON tasks (status);
```
---
## API Endpoints
**POST** `/tasks`
**Request**
```json
{ "title": "Example Task", "payload": { "value": 42 } }
```
**Response**
```json
{ "task_id": "uuid", "status": "PENDING" }
```

**Flow**
1. Insert row into MySQL
2. Publish `task.created`
3. Return `task_id`

---
**GET** `/tasks/{task_id}`
**Response**
```json
{
  "task_id": "uuid",
  "title": "Example Task",
  "status": "DONE",
  "created_at": "...",
  "updated_at": "...",
  "finished_at": null
}
```
---
**WebSocket** `/ws`
* Client receives a broadcast stream of all task status updates via Redis Pub/Sub.

* Example Push:
    ```json
    {
    "task_id": "uuid",
    "status": "DONE",
    "updated_at": "2025-10-13T02:31:00Z"
    }
    ```
---
## Folder Structure
```bash
taskflow/
  frontend/
    src/
    Dockerfile
    package.json
  service_api/
    app.py
    api/
      routes_tasks.py
      routes_ws.py
    domain/
      schemas.py
    infra/
      db.py          # Async MySQL (SQLAlchemy)
      mq.py          # RabbitMQ producer (aio-pika)
      cache.py       # Redis (aioredis)
      pubsub.py      # Redis → WebSocket bridge
    tests/
      test_tasks_api.py
    Dockerfile
  service_worker/
    worker.py        # RabbitMQ consumer
    infra/
      db.py
      mq.py
      cache.py
    Dockerfile
  deploy/
    docker-compose.yml
    env.example
  .github/workflows/
    ci.yml
  README.md
```
---
## Environment Variables
```ini
# API
API_PORT=8000
DB_URL=mysql+asyncmy://user:pass@mysql:3306/taskflow
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
DB_CONNECT_ATTEMPTS=10
DB_CONNECT_BACKOFF=2.0
CORS_ALLOW_ORIGINS=*

# Worker
WORKER_PREFETCH=8
RABBITMQ_CONNECT_ATTEMPTS=10
RABBITMQ_CONNECT_BACKOFF=2.0
DB_CONNECT_ATTEMPTS=10
DB_CONNECT_BACKOFF=2.0

# Frontend (optional overrides when running locally)
# REACT_APP_API_BASE=http://localhost:8000
# REACT_APP_WS_URL=ws://localhost:8000/ws
```
---
## docker-compose Services
| Service    | Description                   |
| ---------- | ----------------------------- |
| `api`      | FastAPI REST API (Uvicorn)    |
| `worker`   | Task consumer                 |
| `frontend` | React dashboard (Vite dev)    |
| `migrate`  | Alembic migrations job        |
| `mysql`    | Persistent task DB            |
| `redis`    | Pub/Sub for real-time updates |
| `rabbitmq` | Message broker for tasks      |

> The `migrate` service runs `alembic upgrade head` on startup and exits once it succeeds. The `api` (launching `uvicorn --reload` for rapid iteration) and `worker` services wait until this service finishes before starting.

### Manual Migration

```bash
docker compose --project-directory deploy -f deploy/docker-compose.yml run --rm migrate
```

### Frontend

Once the stack is running, open `http://localhost:5001` to:

- View the full task list and select tasks for detail view
- Create new tasks which will immediately appear in the list
- Observe live updates as the worker pushes state changes over WebSocket

---
## End-to-End Flow
**A) Create Task**
1. POST /tasks → insert row (PENDING)
2. API publishes MQ event task.created
3. Worker consumes → updates to PROCESSING
4. Worker simulates job → updates to DONE/FAILED
5. Worker publishes Redis message
6. API WebSocket relays to client

**B) Poll Task**
* GET /tasks/{id} → returns current MySQL state
---

## Reliability & Observability
* **Idempotency:** Worker checks status before re-updating
* **Retries:** MQ consumer supports exponential backoff
* **Tracing:** Logs include `task_id`, processing duration, and states
* **Health Check:** `/healthz` endpoint pings DB, MQ, Redis
---

## Testing
* **Unit Tests:**
    * POST `/tasks` inserts & publishes
    * GET `/tasks/{id}` returns correct state

* **Integration (docker-compose):**
    * Start full stack → create task → Worker processes → WS receives DONE event
---
## AI-assisted Development
| Stage               | AI Role                                            | Benefit                     |
| ------------------- | -------------------------------------------------- | --------------------------- |
| Architecture design | ChatGPT suggested full microservice flow           | Reduced planning time       |
| CRUD & schema       | ChatGPT generated FastAPI routes & Pydantic models | 1.5h saved                  |
| MQ integration      | Copilot completed async producer/consumer          | 2h saved                    |
| Testing & CI        | ChatGPT produced pytest + Actions YAML             | 1h saved                    |
| Documentation       | ChatGPT generated README & diagrams                | 1h saved                    |
| **Total**           | —                                                  | **~65% faster development** |
---
## Future Enhancements
* Replace Worker with Kubernetes Jobs for scalable processing

* Add Prometheus metrics (queue depth, task duration)

* Implement Dead-letter queue for failed tasks

* Build a simple web dashboard to visualize task lifecycle
---
## Summary
TaskFlow demonstrates how AI-assisted tools can:

* Rapidly bootstrap a production-like backend system
* Handle asynchronous, event-driven workloads
* Combine multiple microservices with minimal boilerplate

🧠 Built with FastAPI, RabbitMQ, Redis, MySQL — and a little help from AI.
