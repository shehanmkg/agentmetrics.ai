# In app/agents/__init__.py
from .query_interpreter import QueryInterpreterAgent, InterpreterOutput
from .data_analysis_agent import DataAnalysisAgent, AnalysisResult
from .insight_generator_agent import InsightGeneratorAgent, GeneratedInsight # Add this line

__all__ = [
    "QueryInterpreterAgent",
    "InterpreterOutput",
    "DataAnalysisAgent",
    "AnalysisResult",
    "InsightGeneratorAgent", # Add this
    "GeneratedInsight"     # Add this
]