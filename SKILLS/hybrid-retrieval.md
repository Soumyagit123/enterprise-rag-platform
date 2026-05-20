# Hybrid Retrieval Skill

**Objective:**
Combine exact keyword matching with semantic understanding.

**Execution:**
1. User provides query.
2. Fire two async tasks simultaneously:
   - Task A: Embed query via Gemini -> Query Pinecone (Dense).
   - Task B: Query BM25 index (Sparse) (this might be hosted in Pinecone or Elasticsearch/local).
3. Wait for both tasks.
4. Merge results. Calculate a combined score: lpha * dense_score + (1 - alpha) * sparse_score (Reciprocal Rank Fusion is often better).
5. Deduplicate based on chunk IDs.
6. Pass the Top 30 results to the Reranker.
