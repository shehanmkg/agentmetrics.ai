import pytest
from fastapi.testclient import TestClient
from main import app # Assuming your FastAPI app instance is named 'app' in 'main.py'
from app.api.v1.endpoints.kpi_queries import QueryResponse # Import for response validation
from app.agents.query_interpreter import MockToolOutput # Import for nested model validation

client = TestClient(app)

# Mock the API key dependency
async def override_get_api_key():
    return "test_api_key"

# app.dependency_overrides[get_api_key] = override_get_api_key # This line needs to be adapted if get_api_key is in a different location

def test_process_query_endpoint():
    # First, ensure the dependency override is correctly applied for this test
    # This might require moving the override logic if 'get_api_key' is not directly accessible here
    # For now, assuming 'get_api_key' can be overridden as shown or this test is adapted
    # If 'app.api.deps.get_api_key' is the actual path:
    from app.api import deps
    app.dependency_overrides[deps.get_api_key] = override_get_api_key

    user_query = "What are the current marketing campaign ROIs?"
    response = client.post(
        "/api/v1/queries/",
        json={"query": user_query}
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["query"] == user_query

    # Validate the agent_response part
    agent_response = response_data["agent_response"]
    expected_interpreted_query = f"Interpreted: '{user_query}' - looking for relevant KPI data."
    expected_data_summary = "Mock data summary: Found 2 relevant datasets for sales and marketing."

    assert agent_response["interpreted_query"] == expected_interpreted_query
    assert agent_response["data_summary"] == expected_data_summary

    # Clean up the dependency override after the test
    app.dependency_overrides = {}
