import os
import shutil
import json
import structlog
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any

from task_queue.producer import producer as queue_producer
from graph.workflow import rag_workflow
from services.cache import semantic_cache
from services.retrieval import retrieval_service
from services.llm import llm_service
from services.guardrails import guardrails_service
from api.middleware import limiter

logger = structlog.get_logger()
router = APIRouter()

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    query: str
    tenant_id: str

@router.post("/ingest")
@limiter.limit("5/minute")  # Heavy job: PDF parse + RabbitMQ queue — 5 uploads/min/IP
async def ingest_document(request: Request, file: UploadFile = File(...), tenant_id: str = Form(...)):
    """
    Accepts a document upload, saves it temporarily, and queues it for async background ingestion.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    file_path = os.path.join(UPLOAD_DIR, f"{tenant_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Push to RabbitMQ for processing
        queue_producer.publish_ingestion_job(file_path, file.filename, tenant_id)
        
        logger.info("document_queued", filename=file.filename, tenant_id=tenant_id)
        return {"status": "success", "message": f"Document {file.filename} queued for ingestion."}
        
    except Exception as e:
        logger.error("ingestion_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to queue document.")

@router.post("/chat")
@limiter.limit("20/minute")  # Standard chat — 20 queries/min/IP
async def chat_with_agent(request: Request, request_body: ChatRequest):
    """
    Invokes the LangGraph RAG workflow to answer a user query based on their tenant data.
    """
    try:
        # Run the workflow
        # .ainvoke returns the final state of the graph
        result = await rag_workflow.ainvoke({
            "query": request_body.query,
            "tenant_id": request_body.tenant_id,
            "cache_hit": False,
            "final_response": None,
            "retrieved_docs": [],
            "is_safe": True,
            "errors": []
        })
        
        return {
            "query": request_body.query,
            "response": result.get("final_response"),
            "is_safe": result.get("is_safe"),
            "cache_hit": result.get("cache_hit")
        }
    except Exception as e:
        logger.error("chat_workflow_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate response.")

@router.post("/chat/stream")
@limiter.limit("10/minute")  # Most expensive: LLM streaming + Cohere — 10 req/min/IP
async def chat_with_agent_stream(request: Request, request_body: ChatRequest):
    """
    Streams the LangGraph RAG response in real-time by executing the Compiled Graph's official astream_events API.
    """
    initial_state = {
        "query": request_body.query,
        "tenant_id": request_body.tenant_id,
        "cache_hit": False,
        "final_response": None,
        "retrieved_docs": [],
        "is_safe": True,
        "errors": []
    }
    
    async def event_generator():
        try:
            # We call LangGraph's native astream_events API to run the compiled workflow!
            async for event in rag_workflow.astream_events(initial_state, version="v2"):
                event_type = event["event"]
                event_name = event["name"]
                
                # Check for token chunks natively fired by the chat model inside generate_node
                if event_type == "on_chat_model_stream":
                    token = event["data"]["chunk"].content
                    if token:
                        yield f"data: {json.dumps({'chunk': token, 'is_safe': True})}\n\n"
                        
                # Check for cached results or guardrails blocks in node completion!
                elif event_type == "on_chain_end" and event_name == "LangGraph":
                    final_state = event["data"]["output"]
                    if final_state.get("cache_hit") or not final_state.get("is_safe"):
                        response_text = final_state.get("final_response", "")
                        payload = {
                            "chunk": response_text,
                            "cache_hit": final_state.get("cache_hit"),
                            "is_safe": final_state.get("is_safe")
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            logger.error("stream_failed", error=str(e))
            yield f"data: {json.dumps({'chunk': f'Error occurred: {str(e)}', 'is_safe': False})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

