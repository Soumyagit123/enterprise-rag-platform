# Backend Agent

**Responsibilities:**
- Build and maintain the FastAPI application.
- Implement API routers, Pydantic validation schemas, and dependency injection.
- Integrate rate limiting, IP blocking, and authentication middlewares.
- Manage database connections (Redis, RabbitMQ).

**Stack:**
- Python 3.11+, FastAPI, Uvicorn, Pydantic, Redis-py, Pika (RabbitMQ).

**Constraints:**
- Must use asynchronous code (sync def) for all I/O bound operations.
- Must implement robust error handling (FastAPI exception handlers).
