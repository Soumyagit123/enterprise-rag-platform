# Observability Skills & Patterns

**Logging:**
Use structlog or standard logging with JSON formatters. Include 	race_id, user_id, and 	enant_id in every log.

**Metrics:**
Use the prometheus_client library. Track:
- ag_request_latency_seconds (Histogram)
- ag_cache_hits_total (Counter)
- llm_token_usage_total (Counter)
- pinecone_query_latency_seconds (Histogram)

**Tracing:**
Initialize LangSmith with LANGCHAIN_TRACING_V2=true. Decorate complex internal functions with @traceable.
