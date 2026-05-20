# Parent-Child Retrieval Skill

**Objective:**
Maximize retrieval precision without losing the surrounding context needed by the LLM.

**Execution:**
1. During ingestion, split a document into large "Parent" chunks (e.g., 2000 tokens).
2. Split each Parent chunk into smaller "Child" chunks (e.g., 400 tokens).
3. Embed and store the *Child* chunks in Pinecone. The metadata of the child MUST contain parent_id.
4. Store the *Parent* chunks in a key-value store (like Redis or a document DB) mapped by parent_id.
5. During retrieval, Pinecone returns the most relevant Child chunks.
6. Look up the corresponding Parent chunks using parent_id and send the Parent chunks to the LLM.
