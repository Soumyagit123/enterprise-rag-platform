$BaseDir = "d:\RAG-production-pipeline\enterprise-rag-platform"

$Directories = @(
    "AGENTS", "SKILLS", "TASKS", "WORKFLOWS", "CHECKLISTS", "MEMORY",
    "backend", "frontend", "infrastructure", "docker", "tests", "docs", "scripts"
)

foreach ($dir in $Directories) {
    New-Item -ItemType Directory -Force -Path "$BaseDir\$dir" | Out-Null
}

$Files = @{
    "MISSION.md" = @"
# Enterprise RAG Platform Mission

## Global Product Goal
Build a production-grade enterprise RAG system that goes beyond simple AI demonstrations. It must support high-throughput, low-latency, and highly accurate document retrieval while mitigating hallucinations and enforcing strict enterprise security.

## Core Capabilities
- **Latency**: Sub-second retrieval and reranking latency.
- **Accuracy**: High retrieval accuracy via Hybrid Search (BM25 + Pinecone Dense Vectors) and Context Compression (Parent-Child chunking).
- **Caching**: Multi-layer Redis Semantic Caching to reduce redundant LLM calls and vector searches.
- **Observability**: Complete transparency into system health using LangSmith, Phoenix Arize, Grafana, and Prometheus.
- **Resilience**: Asynchronous architecture via RabbitMQ, scalable deployments via Docker, and robust retry mechanisms using LangGraph.
- **Guardrails**: Prompt injection defense and hallucination mitigation using Llama Guard and NeMo Guardrails.
- **Multi-Tenant Isolation**: Ensuring data separation via namespace and metadata filtering in Pinecone.

## Primary Stack
- **Frontend**: Next.js
- **Backend**: FastAPI
- **Orchestration**: LangGraph
- **LLM**: Google Gemini
- **Embeddings**: Gemini Embeddings
- **Vector DB**: Pinecone
- **Reranker**: Cohere Rerank
- **Cache**: Redis
- **Queue**: RabbitMQ
- **Containerization**: Docker

## Engineering Standards
- All code must be strongly typed (Pydantic/MyPy).
- All workflows must be observable, retry-safe, and tested.
- All APIs must handle rate-limiting, authentication, and validation.
"@

    "ARCHITECTURE.md" = @"
# Architecture Blueprint

This document outlines the system architecture of the Enterprise RAG Platform.

## 1. High-Level Flow

1.  **Frontend (Next.js)** sends a user query via HTTPS to the API Gateway.
2.  **API Gateway (FastAPI)** validates the request, checks rate limits, and authenticates the user.
3.  **LangGraph Orchestration** manages the lifecycle of the request:
    *   **Query Classifier / Rewriter**: Analyzes intent and rewrites the query for optimal retrieval.
    *   **Cache Check (Redis)**: Checks semantic cache for previous identical queries.
    *   **Hybrid Retrieval**: Searches Pinecone (Dense) + BM25 (Sparse) in parallel.
    *   **Reranking (Cohere)**: Reranks the top 30 retrieved chunks down to the top 5 most relevant.
    *   **Context Compression**: Uses parent-child chunking to expand context while minimizing token overhead.
    *   **Guardrails**: Pre-generation check for malicious prompts (Llama Guard).
    *   **LLM Generation**: Streams a response using Gemini LLM.
    *   **Post-Validation**: Checks for hallucinations using NeMo Guardrails.

## 2. Ingestion Pipeline
*   **Document Loader**: Async ingestion of PDF, HTML, etc.
*   **Queue**: RabbitMQ queues the background parsing and embedding generation.
*   **Chunking**: RecursiveCharacterTextSplitter generates small child chunks and large parent chunks.
*   **Vectorization**: Gemini Embeddings normalize vectors and insert them into Pinecone with proper tenant-isolated namespaces and metadata.

## 3. Deployment Topology
*   **Docker Compose**: Used for local and staging environments. Orchestrates FastAPI, Next.js, Redis, RabbitMQ, Grafana, and Prometheus.
*   **Kubernetes (Future)**: Will replace Docker Compose for horizontal pod autoscaling.

## 4. Observability and Monitoring
*   **LangSmith**: Used for tracing the execution graph inside LangGraph.
*   **Phoenix Arize**: Evaluates hallucination and retrieval quality on the fly.
*   **Grafana & Prometheus**: Gathers API metrics, latency profiles, cache hit rates, and error logs.
"@

    "ROADMAP.md" = @"
# Enterprise RAG Platform Roadmap

## Phase 1: Foundation (Current)
- Establish repository structure, agent skills, memory, and governance files.
- Setup FastAPI and Next.js skeletons.
- Configure Docker and basic environment variables.

## Phase 2: Ingestion & Storage
- Setup RabbitMQ background tasks.
- Implement Parent-Child chunking.
- Integrate Gemini Embeddings and Pinecone.

## Phase 3: Core RAG Mechanics
- Hybrid Search (BM25 + Dense).
- Cohere Reranking.
- Redis Semantic Cache integration.

## Phase 4: LangGraph Orchestration & Guardrails
- Construct the main RAG graph with conditional branching.
- Implement timeout handling and retries.
- Add Llama Guard and NeMo Guardrails.

## Phase 5: Observability & Production Readiness
- Complete LangSmith, Phoenix Arize, Grafana, and Prometheus integration.
- Implement rate-limiting, IP limiting, and API key validation.
- Extensive unit and integration testing.

## Future Horizons
- Migration to Kubernetes.
- Agentic tool use (giving LangGraph tools like SQL databases and web search).
- Fine-tuned small language models for routing and classification to save costs.
"@

    "TECH_STACK.md" = @"
# Detailed Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Next.js | Server-side rendering, React components, UX |
| **Backend API** | FastAPI | Async Python framework, high performance, OpenAPI |
| **Orchestration** | LangGraph | State management, retry loops, conditional execution |
| **Language Model** | Google Gemini | Generation, reasoning, streaming responses |
| **Embeddings** | Gemini Embeddings | Converting text to dense vector space |
| **Vector DB** | Pinecone | Storing and retrieving dense vectors quickly |
| **Sparse Index** | BM25 | Exact keyword matching for Hybrid Search |
| **Reranker** | Cohere Rerank | Deep semantic relevance scoring (Top 30 -> Top 5) |
| **Caching** | Redis (Stack) | Semantic caching, token bucket rate limiting |
| **Message Queue** | RabbitMQ | Async background ingestion and heavy jobs |
| **Tracing** | LangSmith | Inspecting LLM calls and LangGraph state |
| **Evaluation** | Phoenix Arize | RAG specific evaluation (hallucinations, recall) |
| **Metrics** | Prometheus & Grafana| Dashboarding system health (latency, 5xx errors) |
| **Guardrails** | Llama Guard & NeMo | Safety filtering, conversational boundaries, output validation |
| **Deployment** | Docker | Containerization and environment consistency |
"@

    "ANTIGRAVITY.md" = @"
# AntiGravity Instructions (Master Prompt)

As AntiGravity, you are a principal AI engineering organization building a production-grade enterprise RAG platform.

## Execution Requirements
- Always read `MISSION.md`, `ARCHITECTURE.md`, and relevant files in `AGENTS/` and `SKILLS/` before executing tasks.
- **Decompose** complex tasks into smaller subtasks and assign them to specialized agents (e.g., frontend-agent, backend-agent, infra-agent).
- Execute in parallel where possible using concurrent tools.
- **Validate** all outputs before committing.
- Run testing workflows and document architecture decisions in `MEMORY/architecture-decisions.md`.

## Engineering Rules
1.  **Never generate placeholder code**. If you create a file, flesh it out completely based on context.
2.  **Prefer async execution**. Use async/await for FastAPI, Pinecone, LLMs, and cache calls.
3.  **Always add retries**. Network boundaries (LLMs, Vector DBs) fail. Use tenacity or LangGraph retries.
4.  **Always add logging**. Use structured JSON logging for all major execution points.
5.  **Use structured configs**. Use `pydantic-settings` for environment variables.
6.  **All APIs require validation**. Use Pydantic models extensively.
7.  **Optimize for observability**. Expose Prometheus metrics endpoints.
8.  **Avoid giant files**. Keep modules small and single-responsibility.
"@

    "AGENTS\architect-agent.md" = @"
# Architect Agent

**Responsibilities:**
- Define system design, data flow, and API contracts.
- Ensure all services (FastAPI, Next.js, Redis, RabbitMQ, Pinecone) integrate seamlessly.
- Make trade-off decisions regarding latency vs. accuracy vs. cost.
- Update `ARCHITECTURE.md` and `MEMORY/architecture-decisions.md` as the system evolves.

**Constraints:**
- Do not optimize prematurely, but always design for multi-tenancy and horizontal scalability.
- Ensure a clear separation of concerns (e.g., Ingestion vs. Retrieval vs. Generation).
"@

    "AGENTS\backend-agent.md" = @"
# Backend Agent

**Responsibilities:**
- Build and maintain the FastAPI application.
- Implement API routers, Pydantic validation schemas, and dependency injection.
- Integrate rate limiting, IP blocking, and authentication middlewares.
- Manage database connections (Redis, RabbitMQ).

**Stack:**
- Python 3.11+, FastAPI, Uvicorn, Pydantic, Redis-py, Pika (RabbitMQ).

**Constraints:**
- Must use asynchronous code (`async def`) for all I/O bound operations.
- Must implement robust error handling (FastAPI exception handlers).
"@

    "AGENTS\rag-agent.md" = @"
# RAG Agent

**Responsibilities:**
- Develop the LangGraph orchestration engine.
- Implement Parent-Child chunking and Unstructured document loading.
- Build the Hybrid Retrieval system (BM25 + Pinecone).
- Integrate Cohere Reranking.
- Develop Context Compression and Deduction logic.
- Integrate Llama Guard and NeMo Guardrails.
- Handle Gemini LLM generation and streaming.

**Stack:**
- LangChain, LangGraph, Pinecone SDK, Cohere SDK, Google GenAI SDK.

**Optimization Goals:**
- Minimize token usage (cost).
- Maximize context relevance (accuracy).
- Reduce hallucination to near zero.
"@

    "AGENTS\infra-agent.md" = @"
# Infra & DevOps Agent

**Responsibilities:**
- Create and maintain `docker-compose.yml` and `Dockerfile` configurations.
- Ensure RabbitMQ and Redis are properly configured for production (persistence, memory limits).
- Prepare the system for Kubernetes migration.
- Write deployment scripts.

**Constraints:**
- Keep Docker images small (multi-stage builds, alpine/slim variants).
- Never hardcode secrets; always use environment variables.
"@

    "AGENTS\observability-agent.md" = @"
# Observability Agent

**Responsibilities:**
- Implement tracing with LangSmith across all LangGraph nodes.
- Setup Phoenix Arize for retrieval evaluation and hallucination detection.
- Configure Prometheus to scrape metrics from FastAPI and Next.js.
- Create Grafana dashboards for latency, error rates, cache hit ratios, and token usage.

**Constraints:**
- Tracing should not add significant latency overhead to the main execution path.
- Metrics must be cleanly tagged for multi-tenant analysis.
"@

    "AGENTS\frontend-agent.md" = @"
# Frontend Agent

**Responsibilities:**
- Build the Next.js web application for user interactions.
- Implement a chat interface capable of handling Server-Sent Events (SSE) for streaming Gemini responses.
- Develop dashboards for uploading documents (ingestion) and viewing status.
- Apply modern, professional aesthetics (responsive, dark mode, smooth micro-animations).

**Stack:**
- Next.js (App Router), React, Tailwind CSS (if authorized, else Vanilla CSS), Framer Motion for animations.

**Constraints:**
- Must handle loading states, stream interruptions, and error boundaries gracefully.
"@

    "SKILLS\fastapi-patterns.md" = @"
# FastAPI Skills & Patterns

**Async/Await:**
Always use `async def` for endpoint definitions unless performing heavy CPU-bound tasks (which should be sent to RabbitMQ). Use `httpx` instead of `requests` for outgoing HTTP calls.

**Dependency Injection:**
Use `Depends()` for database connections, authentication verification, and rate limiting logic. This makes testing much easier.

**Pydantic Settings:**
Use `pydantic_settings.BaseSettings` for environment variable management. It provides type safety and automatic `.env` file reading.

**Error Handling:**
Use `raise HTTPException(status_code=...)` for expected errors, but also register global exception handlers for unexpected 500 errors to ensure they are logged and return a clean JSON response.
"@

    "SKILLS\langgraph-patterns.md" = @"
# LangGraph Skills & Patterns

**State Management:**
Define a strict `TypedDict` or Pydantic model for the Graph State. Ensure it tracks `query`, `retrieved_docs`, `reranked_docs`, `cache_hit`, `final_answer`, and `errors`.

**Conditional Edges:**
Use conditional edges heavily. E.g., `check_cache` node -> if hit, go to `generate_response`; if miss, go to `retrieve`.

**Retries:**
Wrap unreliable nodes (like API calls to LLMs or Vector DBs) with retry logic or define fallback nodes in the graph in case of timeouts.
"@

    "SKILLS\hybrid-retrieval.md" = @"
# Hybrid Retrieval Skill

**Objective:**
Combine exact keyword matching with semantic understanding.

**Execution:**
1. User provides query.
2. Fire two async tasks simultaneously:
   - Task A: Embed query via Gemini -> Query Pinecone (Dense).
   - Task B: Query BM25 index (Sparse) (this might be hosted in Pinecone or Elasticsearch/local).
3. Wait for both tasks.
4. Merge results. Calculate a combined score: `alpha * dense_score + (1 - alpha) * sparse_score` (Reciprocal Rank Fusion is often better).
5. Deduplicate based on chunk IDs.
6. Pass the Top 30 results to the Reranker.
"@

    "SKILLS\redis-semantic-cache.md" = @"
# Redis Semantic Cache Skill

**Objective:**
Avoid redundant work for semantically identical queries.

**Execution:**
- Use Redis Vector Search capabilities.
- When a query arrives, embed it and search Redis for embeddings with cosine similarity > 0.95.
- **Embedding Cache (TTL 7d):** Cache text-to-embedding mappings to save Gemini API calls during ingestion.
- **Retrieval Cache (TTL 1d):** Cache query-to-retrieved-documents mappings to skip Pinecone search.
- **Response Cache (TTL 6h):** Cache query-to-LLM-response mappings to skip generation entirely if a very similar query was recently asked.
"@

    "SKILLS\parent-child-retrieval.md" = @"
# Parent-Child Retrieval Skill

**Objective:**
Maximize retrieval precision without losing the surrounding context needed by the LLM.

**Execution:**
1. During ingestion, split a document into large "Parent" chunks (e.g., 2000 tokens).
2. Split each Parent chunk into smaller "Child" chunks (e.g., 400 tokens).
3. Embed and store the *Child* chunks in Pinecone. The metadata of the child MUST contain `parent_id`.
4. Store the *Parent* chunks in a key-value store (like Redis or a document DB) mapped by `parent_id`.
5. During retrieval, Pinecone returns the most relevant Child chunks.
6. Look up the corresponding Parent chunks using `parent_id` and send the Parent chunks to the LLM.
"@

    "SKILLS\cohere-reranking.md" = @"
# Cohere Reranking Skill

**Objective:**
Improve precision by deeply comparing the query against a wide initial retrieval set.

**Execution:**
1. Receive Top 30 chunks from Hybrid Retrieval.
2. Format them into the `documents` array required by the Cohere Rerank API.
3. Call `cohere.Client().rerank(query=..., documents=..., top_n=5)`.
4. Handle rate limits and timeouts via retries.
5. Return the heavily filtered Top 5 chunks to be passed into the Context Compressor or LLM.
"@

    "SKILLS\observability-patterns.md" = @"
# Observability Skills & Patterns

**Logging:**
Use `structlog` or standard `logging` with JSON formatters. Include `trace_id`, `user_id`, and `tenant_id` in every log.

**Metrics:**
Use the `prometheus_client` library. Track:
- `rag_request_latency_seconds` (Histogram)
- `rag_cache_hits_total` (Counter)
- `llm_token_usage_total` (Counter)
- `pinecone_query_latency_seconds` (Histogram)

**Tracing:**
Initialize LangSmith with `LANGCHAIN_TRACING_V2=true`. Decorate complex internal functions with `@traceable`.
"@

    "TASKS\phase-1-foundation.md" = @"
# Phase 1: Foundation

**Goal:** Establish the baseline structure, APIs, and containers.

**Steps:**
1. Generate Next.js frontend skeleton in `frontend/`.
2. Generate FastAPI backend skeleton in `backend/` with basic health check endpoints.
3. Create a `docker-compose.yml` orchestrating FastAPI, Next.js, Redis, RabbitMQ, Prometheus, and Grafana.
4. Setup `pytest` infrastructure in `tests/`.
5. Create structured logging configuration in the backend.
6. Define `pydantic-settings` for environment variables (API keys, Redis URLs, etc.).

**Validation:**
- Running `docker compose up` brings up all services without crashing.
- Frontend is accessible on port 3000.
- Backend is accessible on port 8000 and `/docs` works.
- `pytest` runs and passes.
"@

    "TASKS\phase-2-ingestion.md" = @"
# Phase 2: Ingestion & Queues

**Goal:** Process documents asynchronously and prepare them for embeddings.

**Steps:**
1. Implement RabbitMQ producer in FastAPI to accept file uploads and queue them.
2. Implement RabbitMQ consumer worker script to process jobs.
3. Create a document parsing service using `Unstructured` (handles PDF, DOCX, HTML).
4. Implement the `Parent-Child Chunking` logic using Langchain's TextSplitters.
5. Setup Redis to temporarily hold Parent chunks during processing.

**Validation:**
- Uploading a PDF to an endpoint successfully queues a job.
- The worker picks up the job and splits the text into Parent and Child chunks correctly, logging the output.
"@

    "WORKFLOWS\implementation-workflow.md" = @"
# Implementation Workflow

This is the standard operating procedure for AntiGravity agents when tackling a Phase.

1. **Plan & Architect**: The Architect Agent reviews the Phase requirements and breaks it down into component-level files.
2. **Decompose & Assign**: Tasks are split (e.g., Backend Agent builds API, Infra Agent writes Dockerfile).
3. **Execute Parallelly**: Agents write their respective code.
4. **Integration**: Code is stitched together, ensuring dependencies (like environment variables and ports) match.
5. **Validate**: Run syntax checks, type checks (`mypy`), and basic tests (`pytest`).
6. **Refactor**: Clean up messy code, enforce error handling and logging.
7. **Document**: Update `MEMORY/implementation-history.md` with what was completed and any deviations from the original plan.
"@

    "CHECKLISTS\production-readiness.md" = @"
# Production Readiness Checklist

Before marking any major feature as complete, ensure:

- [ ] **Async I/O**: No blocking network or disk calls in the main thread.
- [ ] **Retries & Timeouts**: All external calls (Pinecone, Gemini, Cohere) have explicit timeouts and retry logic.
- [ ] **Logging**: All major state changes and errors are logged in JSON format.
- [ ] **Environment Configs**: No hardcoded secrets, everything is in `BaseSettings`.
- [ ] **Health Checks**: Containers have liveness and readiness probes defined.
- [ ] **Rate Limiting**: Endpoints are protected against abuse.
- [ ] **Type Hints**: Code passes MyPy checks.
- [ ] **Test Coverage**: Critical paths are covered by unit and integration tests.
"@

    "MEMORY\architecture-decisions.md" = @"
# Architecture Decision Records (ADRs)

*This file will be updated continuously as the system evolves.*

## ADR-001: Next.js over Angular
**Date**: Initial Planning
**Decision**: Use Next.js instead of Angular for the frontend.
**Reason**: User requested React or Next.js. Next.js provides excellent SSR, API routes for frontend-specific logic, and easy integration with Vercel/Docker.

## ADR-002: Parent-Child Chunking Strategy
**Date**: Initial Planning
**Decision**: Implement Parent-Child chunking instead of standard fixed-size chunking.
**Reason**: To resolve the tension between needing small chunks for highly precise vector retrieval and needing large chunks to provide the LLM with sufficient context to generate a coherent answer.
"@
}

foreach ($item in $Files.GetEnumerator()) {
    $FilePath = "$BaseDir\$($item.Name)"
    Set-Content -Path $FilePath -Value $item.Value -Encoding UTF8
}

Write-Output "Successfully generated files."
