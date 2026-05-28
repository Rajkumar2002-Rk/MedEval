"""
EngineResult: the output of the rules engine for a single patient.

The engine returns this object instead of just an integer level. Reasons:
- We need to know WHICH rules fired, not just the final level, for transparency
  and audit. Medical software must explain its decisions.
- The LLM uses the rationales as raw material when writing the plain-English
  explanation to the patient.
- The decision_path tells us whether the level came from the primary path
  (A/B/C) or from a Decision D vital-sign upgrade.
"""

from pydantic import BaseModel, Field

class EngineResult(BaseModel):
    esi_level: int = Field(ge=1, le=5)
    rules_fired: list[str] = Field(default_factory=list)
    rationales: list[str] = Field(default_factory=list)
    decision_path: str 
    