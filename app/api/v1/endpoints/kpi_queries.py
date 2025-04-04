from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# We'll replace this with actual agent implementation later
from app.api.deps import get_api_key

router = APIRouter()

class QueryRequest(BaseModel):
    """Model for KPI query requests."""
    query: str

class QueryResponse(BaseModel):
    """Model for KPI query responses."""
    results: dict
    query: str

@router.post("/", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Process a natural language query about KPIs.
    
    Currently returns a placeholder response until the agent pipeline is implemented.
    """
    # This is a placeholder - will be replaced with actual agent processing
    return QueryResponse(
        query=query_request.query,
        results={
            "message": "Agent pipeline not yet implemented",
            "query_received": query_request.query
        }
    ) 