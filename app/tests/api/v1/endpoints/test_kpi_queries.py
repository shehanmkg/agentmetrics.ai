# In app/tests/api/v1/endpoints/test_kpi_queries.py
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Ensure main.app is importable, adjust path if your structure differs
from main import app
# Ensure app.api.deps.get_api_key is the correct path
from app.api.deps import get_api_key
from app.agents import InterpreterOutput, AnalysisResult, GeneratedInsight, StructuredQuery

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_api_key_dep_fixture():
    app.dependency_overrides[get_api_key] = lambda: "test_api_key"
    yield
    app.dependency_overrides = {} # Clear overrides after test

@patch('app.api.v1.endpoints.kpi_queries.InsightGeneratorAgent.run', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.kpi_queries.DataAnalysisAgent.run', new_callable=AsyncMock)
@patch('app.api.v1.endpoints.kpi_queries.QueryInterpreterAgent.run', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_query_endpoint_successful_flow_mocked_agents(
    mock_interpreter_run, mock_analyzer_run, mock_insight_run
):
    user_query = "Analyze sales for Q2"
    # Provide all required fields for StructuredQuery, even if empty lists/defaults
    mock_interpreter_run.return_value = InterpreterOutput(
        raw_query=user_query,
        interpretation_summary="Interpreted sales query for Q2.",
        structured_query_representation=StructuredQuery(
            table="kpi_data",
            select_fields=[],
            join_on=[],
            filters=[],
            raw_sql_debug="SELECT ..."
        ),
        fetched_data=[{"KpiData_value": 1000, "KpiDefinition_name": "Q2 Sales"}]
    )
    mock_analyzer_run.return_value = AnalysisResult(
        analyzed_context="kpi_data", record_count=1,
        summary_statistics={"sum_KpiData_value": 1000},
        trends_identified=["Positive trend in Q2 sales."], anomalies_detected=[]
    )
    mock_insight_run.return_value = GeneratedInsight(
        executive_summary="Q2 sales look promising.",
        key_findings=["Total Q2 sales amounted to 1000 units."],
        recommendations=["Continue current strategy."],
        data_context="kpi_data", record_count_analyzed=1
    )

    response = client.post("/api/v1/queries/", json={"query": user_query})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["original_query"] == user_query
    assert response_data["final_insight"]["executive_summary"] == "Q2 sales look promising."

    mock_interpreter_run.assert_called_once_with(user_query=user_query)
    mock_analyzer_run.assert_called_once_with(
        query_context="kpi_data",
        data=[{"KpiData_value": 1000, "KpiDefinition_name": "Q2 Sales"}]
    )
    mock_insight_run.assert_called_once_with(analysis_result=mock_analyzer_run.return_value)

@patch('app.api.v1.endpoints.kpi_queries.QueryInterpreterAgent.run', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_process_query_endpoint_interpreter_failure(mock_interpreter_run):
    user_query = "A query that causes interpreter failure"
    mock_interpreter_run.return_value = InterpreterOutput(
        raw_query=user_query,
        interpretation_summary="Failed to load embedding model.",
        structured_query_representation=None, # Signals failure
        fetched_data=[]
    )
    response = client.post("/api/v1/queries/", json={"query": user_query})
    assert response.status_code == 200
    response_data = response.json()
    assert "Failed to interpret the query." in response_data["final_insight"]["executive_summary"]
    mock_interpreter_run.assert_called_once_with(user_query=user_query)
