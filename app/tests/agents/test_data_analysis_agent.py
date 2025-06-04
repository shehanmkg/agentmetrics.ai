# In app/tests/agents/test_data_analysis_agent.py
import pytest
# import pandas as pd # Not strictly needed for test definition if agent handles types
from app.agents import DataAnalysisAgent, AnalysisResult

SAMPLE_REAL_DATA_SALES = [
    {'KpiData_timestamp': '2023-01-01', 'KpiData_value': 100, 'KpiDefinition_name': 'sales_total'},
    {'KpiData_timestamp': '2023-01-02', 'KpiData_value': 150, 'KpiDefinition_name': 'sales_total'},
    {'KpiData_timestamp': '2023-01-03', 'KpiData_value': 120, 'KpiDefinition_name': 'sales_total'},
]

SAMPLE_REAL_DATA_MARKETING = [
    {'timestamp': '2023-03-01', 'value': 50.5, 'campaign_name': 'Spring Promo'}, # Note 'value' key
    {'timestamp': '2023-03-02', 'value': 65.0, 'campaign_name': 'Spring Promo'},
]

@pytest.mark.asyncio
async def test_data_analysis_agent_real_sales_data():
    agent = DataAnalysisAgent()
    query_context = "sales_data"

    actual_output: AnalysisResult = await agent.run(query_context=query_context, data=SAMPLE_REAL_DATA_SALES)

    assert actual_output.analyzed_context == query_context
    assert actual_output.record_count == 3
    assert actual_output.summary_statistics['sum_of_KpiData_value'] == 370
    assert pytest.approx(actual_output.summary_statistics['mean_of_KpiData_value']) == (370 / 3)

@pytest.mark.asyncio
async def test_data_analysis_agent_real_marketing_data():
    agent = DataAnalysisAgent()
    query_context = "marketing_spend"

    actual_output: AnalysisResult = await agent.run(query_context=query_context, data=SAMPLE_REAL_DATA_MARKETING)

    assert actual_output.analyzed_context == query_context
    assert actual_output.record_count == 2
    assert actual_output.summary_statistics['sum_of_value'] == 115.5
    assert pytest.approx(actual_output.summary_statistics['mean_of_value']) == (115.5 / 2)

@pytest.mark.asyncio
async def test_data_analysis_agent_empty_data_real():
    agent = DataAnalysisAgent()
    query_context = "empty_test"
    input_data = []
    actual_output: AnalysisResult = await agent.run(query_context=query_context, data=input_data)
    assert actual_output.record_count == 0
    assert actual_output.summary_statistics.get("message") == "No data provided for analysis."
