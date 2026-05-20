# Phase 1: Foundation

**Goal:** Establish the baseline structure, APIs, and containers.

**Steps:**
1. Generate Next.js frontend skeleton in rontend/.
2. Generate FastAPI backend skeleton in ackend/ with basic health check endpoints.
3. Create a docker-compose.yml orchestrating FastAPI, Next.js, Redis, RabbitMQ, Prometheus, and Grafana.
4. Setup pytest infrastructure in 	ests/.
5. Create structured logging configuration in the backend.
6. Define pydantic-settings for environment variables (API keys, Redis URLs, etc.).

**Validation:**
- Running docker compose up brings up all services without crashing.
- Frontend is accessible on port 3000.
- Backend is accessible on port 8000 and /docs works.
- pytest runs and passes.
