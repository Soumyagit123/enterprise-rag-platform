# Cohere Reranking Skill

**Objective:**
Improve precision by deeply comparing the query against a wide initial retrieval set.

**Execution:**
1. Receive Top 30 chunks from Hybrid Retrieval.
2. Format them into the documents array required by the Cohere Rerank API.
3. Call cohere.Client().rerank(query=..., documents=..., top_n=5).
4. Handle rate limits and timeouts via retries.
5. Return the heavily filtered Top 5 chunks to be passed into the Context Compressor or LLM.
