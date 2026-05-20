import uuid
import structlog
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .redis_client import redis_client

logger = structlog.get_logger()

# In a real system, you'd use unstructured, e.g.:
# from unstructured.partition.auto import partition

class IngestionService:
    def __init__(self):
        # We want Parent chunks to be large (e.g., ~2000 chars) to provide rich context
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        # We want Child chunks to be small (e.g., ~400 chars) for precise vector matching
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )

    async def process_document(self, file_content: bytes, filename: str, tenant_id: str):
        """
        Parses a document, splits into Parent/Child chunks, and stores Parent chunks in Redis.
        Returns the Child chunks ready for Embedding/Pinecone.
        """
        logger.info("processing_document", filename=filename, tenant_id=tenant_id)
        
        # 1. Parse Document
        if filename.lower().endswith(".pdf"):
            import io
            try:
                from pypdf import PdfReader
            except ImportError:
                logger.info("pypdf_not_found_installing")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf>=4.0.0"])
                from pypdf import PdfReader
            
            logger.info("parsing_pdf", filename=filename)
            try:
                pdf_file = io.BytesIO(file_content)
                reader = PdfReader(pdf_file)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n".join(text_parts)
                logger.info("pdf_parsed_successfully", filename=filename, length=len(text), pages=len(reader.pages))
            except Exception as e:
                logger.error("pdf_parsing_failed", filename=filename, error=str(e))
                raise ValueError(f"Failed to parse PDF document: {str(e)}")
        else:
            # Assuming plain text/utf-8 for other files
            text = file_content.decode("utf-8", errors="ignore")
        
        # 2. Parent Chunking
        parent_docs = self.parent_splitter.create_documents([text])
        
        all_child_chunks = []
        
        for p_doc in parent_docs:
            parent_id = str(uuid.uuid4())
            parent_text = p_doc.page_content
            
            # Store parent in Redis
            parent_metadata = {"filename": filename, "tenant_id": tenant_id}
            await redis_client.store_parent_chunk(parent_id, parent_text, parent_metadata)
            
            # 3. Child Chunking
            child_docs = self.child_splitter.create_documents([parent_text])
            
            for c_doc in child_docs:
                child_metadata = {
                    "parent_id": parent_id,
                    "filename": filename,
                    "tenant_id": tenant_id,
                    "type": "child_chunk",
                    "text": c_doc.page_content
                }
                all_child_chunks.append({
                    "id": str(uuid.uuid4()),
                    "content": c_doc.page_content,
                    "metadata": child_metadata
                })
                
        logger.info("document_processed", filename=filename, parent_chunks=len(parent_docs), child_chunks=len(all_child_chunks))
        
        # At this point, `all_child_chunks` should be sent to the Embedding service 
        # and then stored in Pinecone.
        return all_child_chunks

ingestion_service = IngestionService()
