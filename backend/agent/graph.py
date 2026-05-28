"""
LangGraph wiring for the 3-node triage pipeline.

Nodes:
  1. extract   — LLM call: TriageRequest → ExtractedFacts
  2. triage    — pure Python rules engine: (TriageRequest, ExtractedFacts) → EngineResult
  3. explain   — LLM call: EngineResult → patient-facing message

The state object flows through the graph. Each node reads what it needs and
adds its output to the state. By the end, all fields are populated.

The compiled graph is exposed as the module-level `graph` object so callers
(like the /triage FastAPI endpoint) can import and invoke it directly.
"""

from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

from models import TriageRequest
from rules.facts import ExtractedFacts
from rules.result import EngineResult
from rules.engine import triage as run_rules_engine
from agent.extraction import extract_facts
from agent.explanation import generate_explanation


class TriageState(BaseModel):
    """Shared state passed between nodes in the graph."""
    request: TriageRequest
    facts: ExtractedFacts | None = None
    result: EngineResult | None = None
    explanation: str | None = None


def extraction_node(state: TriageState) -> dict:
    """Node 1: extract structured facts from the patient's complaint."""
    facts = extract_facts(state.request)
    return {"facts": facts}


def triage_node(state: TriageState) -> dict:
    """Node 2: run the deterministic rules engine. NO LLM here."""
    result = run_rules_engine(state.request, state.facts)
    return {"result": result}


def explanation_node(state: TriageState) -> dict:
    """Node 3: ask the LLM to write a patient-facing explanation."""
    explanation = generate_explanation(state.result)
    return {"explanation": explanation}


def build_graph():
    """Construct and compile the LangGraph workflow."""
    workflow = StateGraph(TriageState)

    workflow.add_node("extract", extraction_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("explain", explanation_node)

    workflow.add_edge(START, "extract")
    workflow.add_edge("extract", "triage")
    workflow.add_edge("triage", "explain")
    workflow.add_edge("explain", END)

    return workflow.compile()


graph = build_graph()


def run_triage(request: TriageRequest) -> TriageState:
    """
    Run a full triage pipeline end-to-end.

    Returns a TriageState with all fields populated:
        - request: the original input
        - facts: what the LLM extracted
        - result: the deterministic engine output (level + rationales)
        - explanation: the patient-facing message
    """
    initial = TriageState(request=request)
    final_state = graph.invoke(initial)

    # LangGraph returns a plain dict; wrap it back into a TriageState for type-safety and clean access (final_state.result.esi_level, etc.).
    return TriageState(**final_state)