import structlog
from langgraph.graph import StateGraph, END
from typing import Dict, Any

from .state import GraphState
from services.cache import semantic_cache
from services.retrieval import retrieval_service
from services.llm import llm_service
from services.guardrails import guardrails_service

logger = structlog.get_logger()

# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

async def check_cache_node(state: GraphState) -> Dict[str, Any]:
    """Check if the response is already in the semantic cache."""
    query = state["query"]
    cached_response = await semantic_cache.check_semantic_response_cache(query)
    
    if cached_response:
        return {"cache_hit": True, "final_response": cached_response, "is_safe": True}
    
    return {"cache_hit": False}

async def retrieve_node(state: GraphState) -> Dict[str, Any]:
    """Perform hybrid retrieval, reranking, and parent context expansion."""
    query = state["query"]
    tenant_id = state["tenant_id"]
    
    # We check retrieval cache first to skip Pinecone if possible
    cached_docs = await semantic_cache.check_retrieval_cache(query)
    if cached_docs:
        docs = cached_docs
    else:
        docs = await retrieval_service.retrieve(query, tenant_id)
        if docs:
            await semantic_cache.set_retrieval_cache(query, docs)
        
    return {"retrieved_docs": docs}

async def guardrails_node(state: GraphState) -> Dict[str, Any]:
    """Run safety checks using Llama Guard / NeMo style validation logic."""
    query = state["query"]
    
    safety_result = await guardrails_service.check_prompt_safety(query)
    
    if not safety_result["is_safe"]:
        return {
            "is_safe": False, 
            "final_response": f"Request blocked: {safety_result['reason']}",
            "errors": [safety_result['reason']]
        }
    
    return {"is_safe": True}

async def generate_node(state: GraphState) -> Dict[str, Any]:
    """Generate final response using Gemini."""
    query = state["query"]
    docs = state["retrieved_docs"]
    
    full_response = []
    async for chunk in llm_service.generate_rag_response_stream(query, docs):
        full_response.append(chunk)
        
    response = "".join(full_response)
    
    # Store in response cache for next time
    await semantic_cache.set_semantic_response_cache(query, response)
    
    return {"final_response": response}


# ---------------------------------------------------------
# Edges & Conditional Logic
# ---------------------------------------------------------

def route_after_cache(state: GraphState) -> str:
    """Decide next step after cache check."""
    if state.get("cache_hit"):
        return "END"
    return "guardrails"

def route_after_guardrails(state: GraphState) -> str:
    """Decide next step after guardrails check."""
    if not state.get("is_safe"):
        return "END"
    return "retrieve"


# ---------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------

def build_workflow() -> StateGraph:
    workflow = StateGraph(GraphState)
    
    # Add Nodes
    workflow.add_node("check_cache", check_cache_node)
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    # Add Edges
    workflow.set_entry_point("check_cache")
    
    workflow.add_conditional_edges(
        "check_cache",
        route_after_cache,
        {
            "guardrails": "guardrails",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "guardrails",
        route_after_guardrails,
        {
            "retrieve": "retrieve",
            "END": END
        }
    )
    
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # Compile the graph
    app = workflow.compile()
    return app

rag_workflow = build_workflow()
