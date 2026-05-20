# Architecture Decision Records (ADRs)

*This file will be updated continuously as the system evolves.*

## ADR-001: Next.js over Angular
**Date**: Initial Planning
**Decision**: Use Next.js instead of Angular for the frontend.
**Reason**: User requested React or Next.js. Next.js provides excellent SSR, API routes for frontend-specific logic, and easy integration with Vercel/Docker.

## ADR-002: Parent-Child Chunking Strategy
**Date**: Initial Planning
**Decision**: Implement Parent-Child chunking instead of standard fixed-size chunking.
**Reason**: To resolve the tension between needing small chunks for highly precise vector retrieval and needing large chunks to provide the LLM with sufficient context to generate a coherent answer.
