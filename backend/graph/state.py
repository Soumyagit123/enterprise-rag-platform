from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class GraphState(TypedDict):
    """
    Represents the state of our LangGraph workflow.
    """
    query: str
    tenant_id: str
    
    # Cache states
    cache_hit: bool
    final_response: Optional[str]
    
    # Retrieval states
    retrieved_docs: List[Dict[str, Any]]
    
    # Generation states
    generation_prompt: Optional[str]
    
    # Guardrails
    is_safe: bool
    
    # Error handling
    errors: List[str]
