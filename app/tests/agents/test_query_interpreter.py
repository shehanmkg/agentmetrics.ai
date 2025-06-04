import pytest
from app.agents import QueryInterpreterAgent
from app.agents.query_interpreter import MockToolOutput

@pytest.mark.asyncio
async def test_query_interpreter_agent_mock_response():
    agent = QueryInterpreterAgent()
    user_query = "What were the sales figures for Q2?"
    expected_output = MockToolOutput(
        interpreted_query=f"Interpreted: '{user_query}' - looking for relevant KPI data.",
        data_summary="Mock data summary: Found 2 relevant datasets for sales and marketing."
    )

    actual_output = await agent.run(user_query)

    assert actual_output.interpreted_query == expected_output.interpreted_query
    assert actual_output.data_summary == expected_output.data_summary
