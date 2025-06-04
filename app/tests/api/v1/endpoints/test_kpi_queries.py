# In app/tests/api/v1/endpoints/test_kpi_queries.py
import pytest
from fastapi.testclient import TestClient
from main import app # Your FastAPI app
# Import the final response model from the endpoint, and the nested GeneratedInsight
from app.api.v1.endpoints.kpi_queries import QueryResponse
from app.agents import GeneratedInsight
from app.api import deps # For overriding dependency

client = TestClient(app)

async def override_get_api_key():
    return "test_api_key"

# Apply override for all tests in this module or manage per test
app.dependency_overrides[deps.get_api_key] = override_get_api_key

def test_process_query_endpoint_full_flow_sales():
    user_query = "Analyze sales for Q2" # This should trigger sales mock data
    response = client.post("/api/v1/queries/", json={"query": user_query})

    assert response.status_code == 200

    response_data = response.json()
    # Validate QueryResponse structure
    assert response_data["original_query"] == user_query
    assert "final_insight" in response_data

    final_insight = response_data["final_insight"]
    # Validate GeneratedInsight structure (example checks)
    assert final_insight["data_source_table"] == "sales_data"
    assert isinstance(final_insight["executive_summary"], str)
    assert len(final_insight["executive_summary"]) > 0
    assert isinstance(final_insight["key_findings"], list)
    assert len(final_insight["key_findings"]) > 0
    # Based on mock data, we expect sales specific insights
    assert any("sales" in finding.lower() for finding in final_insight["key_findings"] if isinstance(finding, str))
    assert any("revenue" in finding.lower() for finding in final_insight["key_findings"] if isinstance(finding, str))


def test_process_query_endpoint_full_flow_marketing():
    user_query = "What about marketing campaigns?" # Triggers marketing mock data
    response = client.post("/api/v1/queries/", json={"query": user_query})

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["original_query"] == user_query
    final_insight = response_data["final_insight"]
    assert final_insight["data_source_table"] == "marketing_campaigns"
    assert any("marketing" in finding.lower() for finding in final_insight["key_findings"] if isinstance(finding, str))
    assert any("roi" in finding.lower() for finding in final_insight["key_findings"] if isinstance(finding, str))

# Clean up dependency overrides if they were module-scoped and tests are done
# If TestClient is created per test, override/cleanup per test or use fixtures.
# For simplicity here, assuming it's fine or handled by test runner lifecycle.
# app.dependency_overrides = {} # This would clear it globally
