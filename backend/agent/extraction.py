"""
Extraction node (Node 1 of the LangGraph pipeline).

Reads the patient's TriageRequest and uses the LLM to produce an
ExtractedFacts object that the rules engine can consume.

The LLM is invoked with structured output bound to the ExtractedFacts
Pydantic model — guaranteeing the response shape matches what the
rules engine expects. No JSON parsing, no string regex.
"""

from pathlib import Path

from models import TriageRequest
from rules.facts import ExtractedFacts
from agent.llm import get_llm


PROMPT_PATH = Path(__file__).parent / "prompts" / "extraction.txt"


def load_extraction_prompt() -> str:
    """Read the system prompt from disk. Loaded once at import time below."""
    return PROMPT_PATH.read_text()


# Read the prompt once when the module is imported — avoids re-reading the file on every patient request. The prompt rarely changes at runtime.
SYSTEM_PROMPT = load_extraction_prompt()


def build_user_message(request: TriageRequest) -> str:
    """
    Build the user-facing prompt content from a TriageRequest.

    We include the chief complaint plus structured demographic/vital data so
    the LLM can use both free text AND measured values when deciding which
    facts apply.
    """
    lines = [
        f"Patient age: {request.patient_age} years",
        f"Patient sex: {request.patient_sex.value}",
        f"Self-reported pain severity (0-10): {request.severity}",
    ]
    if request.patient_age_months is not None:
        lines.append(f"Patient age (months): {request.patient_age_months}")
    if request.heart_rate is not None:
        lines.append(f"Heart rate: {request.heart_rate} bpm")
    if request.systolic_bp is not None and request.diastolic_bp is not None:
        lines.append(f"Blood pressure: {request.systolic_bp}/{request.diastolic_bp} mmHg")
    if request.respiratory_rate is not None:
        lines.append(f"Respiratory rate: {request.respiratory_rate} /min")
    if request.oxygen_saturation is not None:
        lines.append(f"Oxygen saturation: {request.oxygen_saturation}%")
    if request.temperature_celsius is not None:
        lines.append(f"Temperature: {request.temperature_celsius} °C")
    if request.medical_history:
        lines.append(f"Medical history: {', '.join(request.medical_history)}")

    lines.append("")
    lines.append("Chief complaint:")
    lines.append(request.complaint)

    return "\n".join(lines)


def extract_facts(request: TriageRequest) -> ExtractedFacts:
    """
    Call the LLM to extract structured facts from the patient's complaint.

    Returns an ExtractedFacts object validated against the Pydantic schema.
    Raises if the LLM call fails or the response cannot be parsed.
    """
    llm = get_llm(temperature=0.0)  # Deterministic for clinical extraction
    structured_llm = llm.with_structured_output(ExtractedFacts)

    response = structured_llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", build_user_message(request)),
        ]
    )

    return response