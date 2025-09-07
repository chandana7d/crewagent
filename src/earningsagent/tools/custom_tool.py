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
        return f"Processed query synchronously: {query}"

    async def _arun(self, query: str) -> str:
        await asyncio.sleep(1)
        return f"Processed query asynchronously: {query}"

custom_tool = CustomTool()
