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
