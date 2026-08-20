# Billing App

A Flask-based billing microservice that consumes order messages from RabbitMQ and persists them into a PostgreSQL database. It also exposes a read-only HTTP API to list stored orders and a health endpoint to report database connectivity.

This service runs a background RabbitMQ consumer thread inside the same container; messages placed on the configured queue are processed and stored as Order records.

## Overview

- Background consumer that reads from RabbitMQ and creates Order rows in Postgres
- Public endpoint to list stored orders under `/api/billing`
- Health endpoint at `/health` that verifies database connectivity
- Database resilience with startup retry loop
- Containerized for deployment (Dockerfile includes HEALTHCHECK)

## Project Structure

```text
billing-app/
├── app/
│   ├── orders.py          # SQLAlchemy models + helper to create orders
│   └── consume_queue.py   # RabbitMQ consumer logic
├── tests/                 # unit and integration tests
├── Dockerfile
├── server.py              # app startup, DB init, consumer thread, health & API
├── requirements.txt
├── requirements-dev.txt
├── .gitlab-ci.yml
└── README.md
```

## Configuration / Environment

Example `.env`:

```env
BILLING_APP_PORT=8000
BILLING_DB_USER=billing
BILLING_DB_PASS=billing_pass
BILLING_DB_NAME=billing_db
BILLING_DB_HOST=postgres
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_QUEUE=orders
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
```

Required variables used by the service:

- `BILLING_APP_PORT` — port the HTTP server listens on (e.g. 8000)
- `BILLING_DB_USER` — Postgres username
- `BILLING_DB_PASS` — Postgres password
- `BILLING_DB_NAME` — Postgres database name
- `BILLING_DB_HOST` — Postgres host
- `RABBITMQ_HOST` — RabbitMQ host
- `RABBITMQ_PORT` — RabbitMQ port (default 5672)
- `RABBITMQ_QUEUE` — queue name to consume (e.g. `orders`)
- `RABBITMQ_USER` — RabbitMQ username
- `RABBITMQ_PASS` — RabbitMQ password

The application composes the SQLALCHEMY_DATABASE_URI as:

postgresql://<BILLING_DB_USER>:<BILLING_DB_PASS>@<BILLING_DB_HOST>:5432/<BILLING_DB_NAME>

## Behaviour

- On startup the app runs a resilience loop that attempts to create/verify database tables. Once successful it starts a daemon thread that connects to RabbitMQ and consumes messages.
- Each RabbitMQ message is expected to be a JSON payload with `user_id`, `number_of_items`, and `total_amount`. Messages are acknowledged on successful processing; on transient DB or RabbitMQ errors the consumer will either requeue or nack depending on the failure type.
- The HTTP API is intentionally read-only (GET) for retrieving stored orders; order creation is handled asynchronously via RabbitMQ.

## API Endpoints

### Health

GET /health

Responses:
- 200 when DB reachable: { "status": "ok", "services": { "database": "up" } }
- 503 when DB unreachable: { "status": "error", "services": { "database": "down" }, "error": "..." }

### Billing (Orders)

GET /api/billing

Response example:

```json
{
  "status": "success",
  "data": [
    { "id": 1, "user_id": 123, "number_of_items": 3, "total_amount": 49.99 }
  ]
}
```

## Local development

1. Create a Python virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. Start Postgres and RabbitMQ for local testing (example using Docker):

```bash
docker run --rm --name billing-postgres -e POSTGRES_USER=billing -e POSTGRES_PASSWORD=billing_pass -e POSTGRES_DB=billing_db -p 5432:5432 postgres:15 &
docker run --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management &
```

3. Export environment variables (or use an `.env`) and run:

```bash
export BILLING_APP_PORT=8000
export BILLING_DB_USER=billing
export BILLING_DB_PASS=billing_pass
export BILLING_DB_NAME=billing_db
export BILLING_DB_HOST=127.0.0.1
export RABBITMQ_HOST=127.0.0.1
export RABBITMQ_PORT=5672
export RABBITMQ_QUEUE=orders
export RABBITMQ_USER=guest
export RABBITMQ_PASS=guest
python server.py
```

The process will initialize DB tables and start a background consumer thread. Use the management UI of RabbitMQ (http://localhost:15672) to push test messages or run the provided integration tests.

Sample RabbitMQ message payload expected by the consumer:

```json
{
  "user_id": 123,
  "number_of_items": 2,
  "total_amount": 19.99
}
```

## Docker

Build the image:

```bash
docker build -t billing-app .
```

Run the container (example):

```bash
docker run --rm -p 8000:8000 \
  -e BILLING_APP_PORT=8000 \
  -e BILLING_DB_USER=billing \
  -e BILLING_DB_PASS=billing_pass \
  -e BILLING_DB_NAME=billing_db \
  -e BILLING_DB_HOST=postgres \
  -e RABBITMQ_HOST=rabbitmq \
  -e RABBITMQ_PORT=5672 \
  -e RABBITMQ_QUEUE=orders \
  -e RABBITMQ_USER=guest \
  -e RABBITMQ_PASS=guest \
  --name billing-app billing-app
```

The Dockerfile includes a HEALTHCHECK that queries `/health` to confirm DB readiness.

## Testing

Run unit tests:

```bash
pytest -v tests/unit --cov=app --cov=server --cov-report=term
```

Run integration tests (uses the docker-compose under tests/integration):

```bash
docker compose -f tests/integration/docker-compose.yml up -d --wait
pytest -v tests/integration
docker compose -f tests/integration/docker-compose.yml down --rmi local
```

## CI/CD

A GitLab CI pipeline is included in `.gitlab-ci.yml` with stages:
- build (installation & compile checks)
- test (unit & integration)
- scan (SonarQube and Trivy)
- package (Docker image build & push)
- deploy (manual ECS deployment for protected branches)
