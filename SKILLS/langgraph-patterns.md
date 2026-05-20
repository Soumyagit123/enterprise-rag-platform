# LangGraph Skills & Patterns

**State Management:**
Define a strict TypedDict or Pydantic model for the Graph State. Ensure it tracks query, etrieved_docs, eranked_docs, cache_hit, inal_answer, and errors.

**Conditional Edges:**
Use conditional edges heavily. E.g., check_cache node -> if hit, go to generate_response; if miss, go to etrieve.

**Retries:**
Wrap unreliable nodes (like API calls to LLMs or Vector DBs) with retry logic or define fallback nodes in the graph in case of timeouts.
