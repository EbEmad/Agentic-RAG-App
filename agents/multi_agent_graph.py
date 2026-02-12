from typing import Optional, TypedDict, Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from .prompts import PLANNER_SYSTEM, RESEARCHER_SYSTEM, WRITER_SYSTEM, CRITIC_SYSTEM, FINALIZER_SYSTEM


class GraphState(TypedDict):
    question: str
    plan: Optional[Dict[str,Any]]
    research_notes: List[str]
    draft: Optional[str]
    critique:Optional[Dict[str, Any]]
    iteration:int
    max_iteration:int

#Define structured outputs
class Plan(BaseModel):
    steps:List[str]=Field(...,description="Short ordered steps for solving the task.")
    key_risks:List=Field(...,description="Major risks/unknowns that should be addressed.")
    desired_output_structure: List[str] = Field(..., description="Headings to include in final answer.")

