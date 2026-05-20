# Production Readiness Checklist

Before moving any code into the production environment, the deployment orchestrator must verify every item on this list.

## 1. Security & Compliance
- [x] **Secret Management:** No API keys (Gemini, Pinecone, Cohere, LangSmith) are hardcoded. `.env.example` provided.
- [x] **Rate Limiting:** FastAPI uses `slowapi` to enforce IP-based rate limiting on all public endpoints.
- [x] **Data Isolation:** All Pinecone vector upserts and queries enforce a strict `tenant_id` namespace.
- [x] **Prompt Injection Defense:** LangGraph routes user queries through `guardrails_node` before embedding or LLM generation.

## 2. Scalability & Resilience
- [x] **Async Ingestion Pipeline:** Document processing and chunking are offloaded to RabbitMQ consumers, preventing HTTP timeouts.
- [x] **Multi-Tier Caching:** Redis Semantic Cache implemented (Embedding: 7 days, Retrieval: 1 day, Response: 6 hours).
- [x] **Retry Mechanisms:** External API calls to Gemini and Cohere use async SDKs that handle transient failures.
- [x] **Dockerized:** Backend, Frontend, Redis Stack, RabbitMQ, and Monitoring are fully containerized in `docker-compose.yml`.

## 3. Retrieval Performance (RAG)
- [x] **Parent-Child Chunking:** LangChain TextSplitters used to separate dense context (Parent in Redis) from precision matching (Child in Pinecone).
- [x] **Hybrid Search:** Both Sparse (BM25) and Dense (Gemini) embeddings are merged and deduplicated.
- [x] **Reranking:** Cohere Rerank model reduces the top 30 chunks down to the top 5 most highly relevant chunks.

## 4. Observability & Testing
- [x] **Tracing:** LangSmith `LANGCHAIN_TRACING_V2` enabled across the entire LangGraph workflow.
- [x] **Metrics:** Prometheus endpoint exposed at `/metrics` with `rag_request_count` and `rag_request_latency_seconds`.
- [x] **Evaluation:** Foundations for RAG Evaluation (Faithfulness/Relevance) set up via Pytest.

## 5. Deployment
- [x] **Backend:** FastAPI container optimized.
- [x] **Frontend:** Next.js UI container ready to consume `NEXT_PUBLIC_API_URL`.

**STATUS: ALL SYSTEMS GO FOR DEPLOYMENT.**
