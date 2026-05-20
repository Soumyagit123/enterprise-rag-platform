# FastAPI Skills & Patterns

**Async/Await:**
Always use sync def for endpoint definitions unless performing heavy CPU-bound tasks (which should be sent to RabbitMQ). Use httpx instead of equests for outgoing HTTP calls.

**Dependency Injection:**
Use Depends() for database connections, authentication verification, and rate limiting logic. This makes testing much easier.

**Pydantic Settings:**
Use pydantic_settings.BaseSettings for environment variable management. It provides type safety and automatic .env file reading.

**Error Handling:**
Use aise HTTPException(status_code=...) for expected errors, but also register global exception handlers for unexpected 500 errors to ensure they are logged and return a clean JSON response.
