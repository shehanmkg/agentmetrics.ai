# In app/tests/agents/test_data_analysis_agent.py
import pytest
from app.agents import DataAnalysisAgent, AnalysisResult
from app.db.mock_db_connector import MOCK_SALES_DATA # Sample input data

@pytest.mark.asyncio
async def test_data_analysis_agent_sales_data():
    agent = DataAnalysisAgent()
    table_name = "sales_data"
    # Use a copy of the mock data to avoid modification issues if any
    input_data = list(MOCK_SALES_DATA)

    actual_output: AnalysisResult = await agent.run(table_name=table_name, data=input_data)

    assert actual_output.analyzed_table == table_name
    assert "total_revenue" in actual_output.summary_statistics
    assert len(actual_output.trends_identified) > 0
    if any(item.get("revenue", 0) > 2000 for item in input_data):
        assert len(actual_output.anomalies_detected) > 0
    assert actual_output.forecast is not None

@pytest.mark.asyncio
async def test_data_analysis_agent_empty_data():
    agent = DataAnalysisAgent()
    table_name = "empty_table"
    input_data = []

    actual_output: AnalysisResult = await agent.run(table_name=table_name, data=input_data)

    assert actual_output.analyzed_table == table_name
    assert actual_output.summary_statistics.get("message") == "No specific analysis performed for this table type."
    assert "No specific trends identified." in actual_output.trends_identified
