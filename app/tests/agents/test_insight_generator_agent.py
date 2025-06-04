# In app/tests/agents/test_insight_generator_agent.py
import pytest
from app.agents import InsightGeneratorAgent, GeneratedInsight, AnalysisResult

@pytest.mark.asyncio
async def test_insight_generator_agent_real_analysis():
    agent = InsightGeneratorAgent()
    # Create a sample AnalysisResult
    analysis_input = AnalysisResult(
        analyzed_context="sales_performance_q1",
        record_count=150,
        summary_statistics={"total_sales": 50000, "average_transaction_value": 333.33},
        trends_identified=["Sales volume increased by 10% compared to last period."],
        anomalies_detected=["Unusually high sales spike on 2023-03-15."]
    )

    actual_output: GeneratedInsight = await agent.run(analysis_input)

    assert actual_output.data_context == "sales_performance_q1"
    assert actual_output.record_count_analyzed == 150
    assert "Sales volume increased by 10%" in " ".join(actual_output.key_findings)
    assert "average_transaction_value - 333.33" in " ".join(actual_output.key_findings)

@pytest.mark.asyncio
async def test_insight_generator_agent_minimal_real_analysis():
    agent = InsightGeneratorAgent()
    analysis_input = AnalysisResult(
        analyzed_context="inventory_levels",
        record_count=50,
        summary_statistics={"items_checked": 50}, trends_identified=[], anomalies_detected=[]
    )
    actual_output: GeneratedInsight = await agent.run(analysis_input)
    assert actual_output.data_context == "inventory_levels"
    assert actual_output.record_count_analyzed == 50
    assert "items_checked - 50" in " ".join(actual_output.key_findings)
