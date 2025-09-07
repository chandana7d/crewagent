# src/earningsagent/tools/custom_tool.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio

class CustomToolInput(BaseModel):
    query: str = Field(..., description="The query to process")

class CustomTool(BaseTool):
    name: str = "custom_tool"
    description: str = "A custom tool for specialized data processing or API calls"
    args_schema = CustomToolInput

    def _run(self, query: str) -> str:
        # Synchronous tool logic here
        # For example, simple text processing
        return f"Processed query synchronously: {query}"

    async def _arun(self, query: str) -> str:
        # Asynchronous tool logic here, e.g., async API call
        await asyncio.sleep(1)
        return f"Processed query asynchronously: {query}"

# Instantiate custom tool for use by agents
custom_tool = CustomTool()
