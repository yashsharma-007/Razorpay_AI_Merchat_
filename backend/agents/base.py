from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from backend.providers.llm_provider import get_llm_provider, LLMProvider

class AgentOutput(BaseModel):
    agent_name: str
    decision: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm_provider: LLMProvider = get_llm_provider()

    async def run(self, input_data: Dict[str, Any]) -> AgentOutput:
        raise NotImplementedError
