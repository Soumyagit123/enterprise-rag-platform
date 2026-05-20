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
