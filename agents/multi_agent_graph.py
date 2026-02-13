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

class Critique(BaseModel):
    issues: List[str]=Field(..., description="Concrete problems with the current draft.")
    missing_points: List[str] = Field(..., description="Important missing considerations.")
    hallucination_risk: List[str]=Field(...,description="Claims that might be risky without sources.")
    score:int=Field(...,ge=0,le=100,description="Overall quality score of the draft.")
    fix_instructions: List[str]=Field(..., description="Actionable steps to improve the draft.")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def planner_node(state:GraphState)->GraphState:
    structured_planner=llm.with_structured_output(Plan)
    plan_obj=structured_planner.invoke([
        SystemMessage(content=PLANNER_SYSTEM),
        HumanMessage(content=state["question"])
    ])
    
    state["plan"]=plan_obj.model_dump()
    return state

def researcher_node(state:GraphState)->GraphState:
    resp=llm.invoke([
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(content=f"Question:\n{state['question']}\n\nPlan:\n{state['plan']}")
    ]).content

    # store as notes (simple split)
    notes=[line.strip("- ").strip() for line in resp.split("\n") if line.strip()]
    state["research_notes"]=notes
    return state
