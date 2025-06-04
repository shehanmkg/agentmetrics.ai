from pydanticai import Agent, Tool
from pydantic import BaseModel, Field

class MockToolOutput(BaseModel):
    interpreted_query: str = Field(..., description="The interpreted version of the user's query")
    data_summary: str = Field(..., description="A summary of the data that would be fetched")

class QueryInterpreterAgent(Agent):
    class Config:
        tools = [
            Tool(name="interpret_query_and_fetch_data")
        ]
        enable_default_tools = False # Disable default tools like CodeInterpreterTool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Mock implementation of the tool
        self._tools["interpret_query_and_fetch_data"] = self._mock_interpret_query_and_fetch_data

    def _mock_interpret_query_and_fetch_data(self, user_query: str) -> MockToolOutput:
        """
        A mock tool that simulates interpreting a user query and fetching data.
        Returns a structured response.
        """
        return MockToolOutput(
            interpreted_query=f"Interpreted: '{user_query}' - looking for relevant KPI data.",
            data_summary="Mock data summary: Found 2 relevant datasets for sales and marketing."
        )

    async def run(self, user_query: str) -> MockToolOutput:
        """
        Runs the agent with the user query.
        """
        # In a real scenario, PydanticAI would select and run the appropriate tool.
        # Here, we directly call our mock tool for simplicity.
        return self._mock_interpret_query_and_fetch_data(user_query)
