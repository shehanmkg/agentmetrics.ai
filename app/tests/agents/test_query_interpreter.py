# In app/tests/agents/test_query_interpreter.py
import pytest
from unittest.mock import patch, MagicMock
import torch # Ensure torch is imported

from app.agents import QueryInterpreterAgent, InterpreterOutput, StructuredQuery
# Assuming SentenceTransformer and util are imported by the agent module
# from sentence_transformers import SentenceTransformer, util # For typing if needed

# Mock the SentenceTransformer model globally for these tests
# This prevents actual model loading during tests
mock_embedding_model = MagicMock()
# Ensure the mock 'encode' returns a tensor, as expected by pytorch_cos_sim
mock_embedding_model.encode.return_value = torch.randn(1, 384)

# Mock util.pytorch_cos_sim
# Ensure it returns a tensor of the correct shape for similarity scores
mock_cos_sim = MagicMock(return_value=torch.tensor([[0.9, 0.1]]))


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    mock_query_chain = MagicMock()
    session.query.return_value = mock_query_chain
    mock_query_chain.join.return_value = mock_query_chain # type: ignore
    mock_query_chain.filter.return_value = mock_query_chain # type: ignore
    mock_row = MagicMock()
    mock_row._asdict.return_value = {"KpiData_value": 100, "KpiDefinition_name": "Test KPI"}
    mock_query_chain.limit.return_value.all.return_value = [mock_row] # type: ignore
    return session

@pytest.fixture
def mock_session_factory(mock_db_session):
    def factory():
        yield mock_db_session
    return factory

@patch('app.agents.query_interpreter.EMBEDDING_MODEL', new=mock_embedding_model)
@patch('app.agents.query_interpreter.util.pytorch_cos_sim', new=mock_cos_sim)
@pytest.mark.asyncio
async def test_query_interpreter_agent_real_data_flow(mock_session_factory, mock_db_session):
    agent = QueryInterpreterAgent(db_session_factory=mock_session_factory)
    user_query = "What is the sales conversion rate for Q2?"

    with patch.object(agent, '_get_semantic_matches', return_value=["kpi_definitions.name", "kpi_data.quarter"]):
        actual_output: InterpreterOutput = await agent.run(user_query)

    assert actual_output.raw_query == user_query
    assert "Semantic search matched query to: kpi_definitions.name, kpi_data.quarter" in actual_output.interpretation_summary
    assert actual_output.structured_query_representation is not None
    mock_db_session.query.assert_called()

    assert actual_output.structured_query_representation.raw_sql_debug is not None
    assert "SELECT" in actual_output.structured_query_representation.raw_sql_debug.upper()

    assert len(actual_output.fetched_data) == 1
    assert actual_output.fetched_data[0]["KpiDefinition_name"] == "Test KPI"

@patch('app.agents.query_interpreter.EMBEDDING_MODEL', new=None)
@pytest.mark.asyncio
async def test_query_interpreter_no_embedding_model(mock_session_factory):
    agent = QueryInterpreterAgent(db_session_factory=mock_session_factory)
    user_query = "Test query"
    output = await agent.run(user_query)
    assert "Error: Embedding model not loaded" in output.interpretation_summary
    assert output.fetched_data == []
