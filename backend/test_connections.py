import os
import sys
import asyncio
import structlog

# Set up simple stdout logger for testing
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

async def test_all():
    logger.info("starting_system_tests")

    # --- 1. Import Verification ---
    logger.info("testing_imports")
    try:
        from api.routes import router as api_router
        from graph.workflow import rag_workflow
        from services.retrieval import retrieval_service
        from services.vector_store import vector_store
        from services.embedding import embedding_service
        from services.llm import llm_service
        from task_queue.producer import producer as queue_producer
        logger.info("imports_successful")
    except Exception as e:
        logger.error("imports_failed", error=str(e), exc_info=True)
        return False

    # --- 2. Pinecone Connection & Auto-creation Test ---
    logger.info("testing_pinecone")
    try:
        from pinecone import Pinecone
        api_key = os.getenv("PINECONE_API_KEY", "")
        index_name = os.getenv("PINECONE_INDEX_NAME", "rag")
        
        if not api_key:
            raise ValueError("PINECONE_API_KEY is missing from environment.")
            
        pc = Pinecone(api_key=api_key)
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        logger.info("pinecone_connected", existing_indexes=existing_indexes)
        
        if index_name not in existing_indexes:
            logger.info("pinecone_index_missing_will_create", index_name=index_name)
            # Pinecone VectorStoreService constructor will handle this automatically during main app run,
            # but let's test creating it or checking it here
        else:
            logger.info("pinecone_index_exists", index_name=index_name)
            
    except Exception as e:
        logger.error("pinecone_failed", error=str(e), exc_info=True)
        return False

    # --- 3. Gemini Embedding Test ---
    logger.info("testing_gemini_embeddings")
    try:
        # Check API key
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        if not gemini_key:
            raise ValueError("GOOGLE_API_KEY / GEMINI_API_KEY is missing from environment.")
            
        from services.embedding import embedding_service
        sample_chunks = [{"id": "test_1", "content": "Hello world from enterprise RAG pipeline", "metadata": {"tenant_id": "test_tenant"}}]
        embedded = await embedding_service.generate_embeddings(sample_chunks)
        
        if embedded and "values" in embedded[0]:
            logger.info("gemini_embeddings_successful", dimension=len(embedded[0]["values"]))
        else:
            raise ValueError("Failed to generate embeddings value key.")
    except Exception as e:
        logger.error("gemini_embeddings_failed", error=str(e), exc_info=True)
        return False

    # --- 4. Gemini LLM Test ---
    logger.info("testing_gemini_llm")
    try:
        from services.llm import llm_service
        sample_context = [{"content": "Enterprise RAG Platform is built by Google DeepMind."}]
        response = await llm_service.generate_rag_response(
            query="Who built the Enterprise RAG Platform?",
            context_docs=sample_context
        )
        logger.info("gemini_llm_successful", response=response)
    except Exception as e:
        logger.error("gemini_llm_failed", error=str(e), exc_info=True)
        return False

    logger.info("all_system_tests_passed")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_all())
    sys.exit(0 if success else 1)
