from pydantic import BaseModel
from typing import Dict, Any


class ToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    result: Dict[str, Any]