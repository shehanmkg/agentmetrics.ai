# In app/tests/agents/test_query_interpreter.py
import pytest
from app.agents import QueryInterpreterAgent, InterpreterOutput
from app.agents.query_interpreter import StructuredQuery # Import for validation
from app.db.mock_db_connector import MOCK_SALES_DATA # For checking fetched_data

@pytest.mark.asyncio
async def test_query_interpreter_agent_sales_query():
    agent = QueryInterpreterAgent()
    user_query = "What were the sales figures for Q2?"

    actual_output: InterpreterOutput = await agent.run(user_query)

    assert actual_output.raw_query == user_query
    assert actual_output.structured_query.table == "sales_data"
    assert actual_output.structured_query.filters == {"quarter": "Q2"}
    assert actual_output.interpretation_summary == "Interpreted as a query for sales data."
    # Check if fetched_data matches the mock sales data for Q2 (currently all mock sales data)
    assert actual_output.fetched_data == MOCK_SALES_DATA
    assert len(actual_output.fetched_data) > 0

@pytest.mark.asyncio
async def test_query_interpreter_agent_unknown_query():
    agent = QueryInterpreterAgent()
    user_query = "Tell me something interesting."

    actual_output: InterpreterOutput = await agent.run(user_query)

    assert actual_output.raw_query == user_query
    assert actual_output.structured_query.table == "unknown"
    assert actual_output.fetched_data == [] # Expect empty list for unknown table
    assert actual_output.interpretation_summary == "Could not determine specific table from query."
