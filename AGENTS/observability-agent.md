# Observability Agent

**Responsibilities:**
- Implement tracing with LangSmith across all LangGraph nodes.
- Setup Phoenix Arize for retrieval evaluation and hallucination detection.
- Configure Prometheus to scrape metrics from FastAPI and Next.js.
- Create Grafana dashboards for latency, error rates, cache hit ratios, and token usage.

**Constraints:**
- Tracing should not add significant latency overhead to the main execution path.
- Metrics must be cleanly tagged for multi-tenant analysis.
