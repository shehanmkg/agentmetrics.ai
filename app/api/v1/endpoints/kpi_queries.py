from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_api_key
from app.agents import QueryInterpreterAgent # Import the agent
from app.agents.query_interpreter import MockToolOutput # Import the response model

router = APIRouter()

class QueryRequest(BaseModel):
    """Model for KPI query requests."""
    query: str

# Update QueryResponse to match the agent's output structure
class QueryResponse(BaseModel):
    """Model for KPI query responses."""
    query: str
    # results: dict # Keep this commented out or remove if not used
    agent_response: MockToolOutput # Add this field for the agent's structured output


@router.post("/", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Process a natural language query about KPIs.
    
    This endpoint now uses the QueryInterpreterAgent to process the query.
    """
    agent = QueryInterpreterAgent()
    agent_output = await agent.run(user_query=query_request.query)

    return QueryResponse(
        query=query_request.query,
        agent_response=agent_output
    )