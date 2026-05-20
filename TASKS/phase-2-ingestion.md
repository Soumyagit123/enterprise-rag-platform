# Phase 2: Ingestion & Queues

**Goal:** Process documents asynchronously and prepare them for embeddings.

**Steps:**
1. Implement RabbitMQ producer in FastAPI to accept file uploads and queue them.
2. Implement RabbitMQ consumer worker script to process jobs.
3. Create a document parsing service using Unstructured (handles PDF, DOCX, HTML).
4. Implement the Parent-Child Chunking logic using Langchain's TextSplitters.
5. Setup Redis to temporarily hold Parent chunks during processing.

**Validation:**
- Uploading a PDF to an endpoint successfully queues a job.
- The worker picks up the job and splits the text into Parent and Child chunks correctly, logging the output.
