import os
import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = structlog.get_logger()

# Gemini configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")

class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_output_tokens=512,  # Reduced from 1024 → faster generation for concise RAG answers
            google_api_key=GEMINI_API_KEY
        )

    async def generate_rag_response(self, query: str, context_docs: list) -> str:
        """
        Generates an answer based strictly on the provided context.
        """
        logger.info("generating_llm_response")
        
        context_str = "\n\n".join([doc.get("content", "") for doc in context_docs])
        
        system_prompt = (
            "You are an expert enterprise AI assistant. "
            "Answer the user's question ONLY using the provided context below. "
            "If you cannot answer the question using the context, say 'I could not find the information in the provided context.'\n\n"
            f"CONTEXT:\n{context_str}"
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        try:
            # We will use streaming in the FastAPI endpoint directly, but for the graph we can do a standard call
            response = await self.llm.ainvoke(messages)
            logger.info("llm_generation_complete")
            return response.content
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise

    async def generate_rag_response_stream(self, query: str, context_docs: list):
        """
        Yields text chunks of the answer as they are generated.
        """
        logger.info("generating_llm_response_stream")
        
        context_str = "\n\n".join([doc.get("content", "") for doc in context_docs])
        
        system_prompt = (
            "You are an expert enterprise AI assistant. "
            "Answer the user's question ONLY using the provided context below. "
            "If you cannot answer the question using the context, say 'I could not find the information in the provided context.'\n\n"
            f"CONTEXT:\n{context_str}"
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        try:
            async for chunk in self.llm.astream(messages):
                yield chunk.content
            logger.info("llm_generation_stream_complete")
        except Exception as e:
            logger.error("llm_generation_stream_failed", error=str(e))
            raise


llm_service = LLMService()
