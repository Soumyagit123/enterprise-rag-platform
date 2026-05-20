# Redis Semantic Cache Skill

**Objective:**
Avoid redundant work for semantically identical queries.

**Execution:**
- Use Redis Vector Search capabilities.
- When a query arrives, embed it and search Redis for embeddings with cosine similarity > 0.95.
- **Embedding Cache (TTL 7d):** Cache text-to-embedding mappings to save Gemini API calls during ingestion.
- **Retrieval Cache (TTL 1d):** Cache query-to-retrieved-documents mappings to skip Pinecone search.
- **Response Cache (TTL 6h):** Cache query-to-LLM-response mappings to skip generation entirely if a very similar query was recently asked.
