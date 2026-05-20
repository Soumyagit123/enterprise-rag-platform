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
