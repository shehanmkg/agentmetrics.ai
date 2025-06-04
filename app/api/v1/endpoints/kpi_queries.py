from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_api_key
# Import all agents and their relevant output models
from app.agents import (
    QueryInterpreterAgent,
    InterpreterOutput,
    DataAnalysisAgent,
    AnalysisResult,
    InsightGeneratorAgent,
    GeneratedInsight
)

router = APIRouter()

class QueryRequest(BaseModel):
    """Model for KPI query requests."""
    query: str

# QueryResponse will now primarily include the final insight and the original query.
# It can also include intermediate results for debugging or more detailed responses if desired.
class QueryResponse(BaseModel):
    """Model for KPI query responses, including the final generated insight."""
    original_query: str
    final_insight: GeneratedInsight
    # Optional: include intermediate step results if useful for client/debugging
    # interpretation_details: Optional[InterpreterOutput] = None
    # analysis_details: Optional[AnalysisResult] = None


@router.post("/", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    api_key: str = Depends(get_api_key) # Assuming get_api_key is correctly set up
):
    """
    Process a natural language query about KPIs through the full agent pipeline.
    """
    # 1. Initialize Agents
    interpreter_agent = QueryInterpreterAgent()
    analysis_agent = DataAnalysisAgent()
    insight_agent = InsightGeneratorAgent()

    # 2. Run Query Interpreter Agent
    interpreter_output: InterpreterOutput = await interpreter_agent.run(
        user_query=query_request.query
    )

    # 3. Run Data Analysis Agent
    # The DataAnalysisAgent expects table_name and data
    analysis_output: AnalysisResult = await analysis_agent.run(
        table_name=interpreter_output.structured_query.table,
        data=interpreter_output.fetched_data
    )

    # 4. Run Insight Generator Agent
    generated_insight: GeneratedInsight = await insight_agent.run(
        analysis_result=analysis_output
    )

    # 5. Return the final response
    return QueryResponse(
        original_query=query_request.query,
        final_insight=generated_insight
        # Optionally include these if they are part of QueryResponse model:
        # interpretation_details=interpreter_output,
        # analysis_details=analysis_output
    )