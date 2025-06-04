from fastapi import APIRouter, Depends, HTTPException # Added HTTPException
from pydantic import BaseModel
from typing import Optional # For optional fields if we re-add them

from app.api.deps import get_api_key
# Import all agents and their relevant output models
from app.agents import (
    QueryInterpreterAgent,
    InterpreterOutput,
    DataAnalysisAgent, # DataAnalysisInput is internal to the agent
    AnalysisResult,
    InsightGeneratorAgent,
    GeneratedInsight  # This now has data_context and record_count_analyzed
)
# Also import StructuredQuery if we need to type hint its presence in InterpreterOutput
from app.agents.query_interpreter import StructuredQuery


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
    # Handle cases where interpretation might not be sufficient
    if not interpreter_output.fetched_data and not interpreter_output.structured_query_representation:
        # This case might indicate a failure in query interpretation or embedding model issue
        # For now, we'll let it flow to analysis, which should handle empty data.
        # A more robust error handling could be added here.
        # Or, if structured_query_representation is None, it means very early failure.
        if interpreter_output.structured_query_representation is None:
            # This implies a severe issue, like embedding model not loading.
            # The agent itself should populate interpretation_summary.
            # We can return a simplified error response or a specific insight.
            # For now, creating a dummy insight.
            error_insight = GeneratedInsight(
                executive_summary="Failed to interpret the query.",
                key_findings=[interpreter_output.interpretation_summary or "No specific error details."],
                recommendations=["Try rephrasing your query or check system logs."],
                data_context=query_request.query, # Use raw query as context
                record_count_analyzed=0
            )
            return QueryResponse(original_query=query_request.query, final_insight=error_insight)


    # 3. Run Data Analysis Agent
    # The DataAnalysisAgent expects `query_context` and `data`.
    # `query_context` can be derived from the interpreter's output.
    query_context_for_analysis = "general_data" # Default context
    if interpreter_output.structured_query_representation and interpreter_output.structured_query_representation.table:
        query_context_for_analysis = interpreter_output.structured_query_representation.table

    analysis_output: AnalysisResult = await analysis_agent.run(
        query_context=query_context_for_analysis,
        data=interpreter_output.fetched_data
    )

    # 4. Run Insight Generator Agent
    generated_insight: GeneratedInsight = await insight_agent.run(
        analysis_result=analysis_output
    )

    # 5. Return the final response
    response_payload = QueryResponse(
        original_query=query_request.query,
        final_insight=generated_insight
    )

    # # Optionally add more debug info if fields exist in QueryResponse
    # if hasattr(response_payload, 'interpretation_summary'):
    #     response_payload.interpretation_summary = interpreter_output.interpretation_summary
    # if hasattr(response_payload, 'structured_sql_query_debug') and interpreter_output.structured_query_representation:
    #     response_payload.structured_sql_query_debug = interpreter_output.structured_query_representation.raw_sql_debug
    # if hasattr(response_payload, 'analysis_summary_stats'):
    #     response_payload.analysis_summary_stats = analysis_output.summary_statistics

    return response_payload