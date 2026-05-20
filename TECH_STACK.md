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
