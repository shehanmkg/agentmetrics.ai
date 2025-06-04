# In app/agents/data_analysis_agent.py
from pydanticai import Agent, Tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# We'll receive data that was fetched by the QueryInterpreterAgent
# It might be useful to also know what kind of data it is (e.g., table name)
class DataAnalysisInput(BaseModel):
    table_name: str
    data: List[Dict[str, Any]] = Field(..., description="Data to be analyzed")

class AnalysisResult(BaseModel):
    analyzed_table: str
    summary_statistics: Dict[str, Any] = Field(default_factory=dict, description="Basic statistics like mean, median, mode if applicable")
    trends_identified: List[str] = Field(default_factory=list, description="Identified trends in the data")
    anomalies_detected: List[str] = Field(default_factory=list, description="Detected anomalies or outliers")
    forecast: Optional[str] = Field(None, description="A simple forecast if applicable")

class DataAnalysisAgent(Agent):
    class Config:
        tools = [
            Tool(name="analyze_data")
        ]
        enable_default_tools = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tools["analyze_data"] = self._mock_analyze_data

    def _mock_analyze_data(self, analysis_input: DataAnalysisInput) -> AnalysisResult:
        """
        Mock tool to analyze data and generate a structured analysis result.
        """
        stats = {}
        trends = []
        anomalies = []
        forecast = None

        if analysis_input.table_name == "sales_data":
            # Calculate mock revenue sum
            total_revenue = sum(item.get("revenue", 0) for item in analysis_input.data)
            stats["total_revenue"] = total_revenue
            stats["average_revenue_per_transaction"] = total_revenue / len(analysis_input.data) if analysis_input.data else 0

            if len(analysis_input.data) > 1:
                trends.append("Positive trend in sales revenue observed over the period.")
            if any(item.get("revenue", 0) > 2000 for item in analysis_input.data):
                anomalies.append("Anomaly: Transaction with revenue > 2000 detected.")
            forecast = "Sales are forecasted to increase by 5% in the next period based on current trends."

        elif analysis_input.table_name == "marketing_campaigns":
            total_spend = sum(item.get("spend", 0) for item in analysis_input.data)
            avg_roi = sum(item.get("roi", 0) for item in analysis_input.data) / len(analysis_input.data) if analysis_input.data else 0
            stats["total_marketing_spend"] = total_spend
            stats["average_roi"] = round(avg_roi, 2)

            if avg_roi > 2.0:
                trends.append("Marketing campaigns show a generally positive ROI.")
            else:
                trends.append("Marketing ROI is moderate, potential for optimization.")
            if any(item.get("roi", 0) < 1.0 for item in analysis_input.data):
                anomalies.append("Anomaly: Campaign with ROI < 1.0 detected, needs review.")
        else:
            stats["message"] = "No specific analysis performed for this table type."
            trends.append("No specific trends identified.")

        return AnalysisResult(
            analyzed_table=analysis_input.table_name,
            summary_statistics=stats,
            trends_identified=trends,
            anomalies_detected=anomalies,
            forecast=forecast
        )

    async def run(self, table_name: str, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Runs the data analysis agent.
        """
        input_data = DataAnalysisInput(table_name=table_name, data=data)
        return self._mock_analyze_data(input_data)
