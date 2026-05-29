"""
MedEval API — FastAPI entry point.

Endpoints:
  GET  /health   — liveness probe
  POST /triage   — run a patient through the full LangGraph triage pipeline

The /triage endpoint accepts a TriageRequest, runs the deterministic rules
engine and the LLM extraction/explanation nodes, and returns the ESI level,
the rules that fired, and a patient-facing message.
"""

from pydantic import BaseModel

from fastapi import FastAPI

from models import TriageRequest
from agent.graph import run_triage
from fastapi import Depends
from security import verify_api_key
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MedEval API",
    version="0.2.0",
    description="Healthcare AI triage assistant. Deterministic rules + LLM explanations.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriageResponse(BaseModel):
    """The public response shape for /triage. Subset of internal TriageState."""
    esi_level: int
    decision_path: str
    rules_fired: list[str]
    explanation: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse, dependencies=[Depends(verify_api_key)])
def triage(request: TriageRequest) -> TriageResponse:
    """
    Triage a patient end-to-end.

    Pipeline:
      1. LLM extracts structured facts from the complaint text
      2. Deterministic rules engine assigns ESI level (1-5)
      3. LLM writes a plain-English explanation for the patient
    """
    state = run_triage(request)
    return TriageResponse(
        esi_level=state.result.esi_level,
        decision_path=state.result.decision_path,
        rules_fired=state.result.rules_fired,
        explanation=state.explanation,
    )