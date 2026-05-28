"""
Explanation node (Node 3 of the LangGraph pipeline).

Takes the EngineResult produced by the rules engine and uses the LLM to
generate a short, plain-English message addressed to the patient.

Safety constraint: the LLM is forbidden from inventing new medical reasoning.
It may ONLY translate the rationales we hand it into patient-friendly language.
"""

from pathlib import Path

from rules.result import EngineResult
from agent.llm import get_llm


PROMPT_PATH = Path(__file__).parent / "prompts" / "explanation.txt"


def load_explanation_prompt() -> str:
    """Read the system prompt from disk."""
    return PROMPT_PATH.read_text()


SYSTEM_PROMPT = load_explanation_prompt()


def build_user_message(engine_result: EngineResult) -> str:
    """Format the EngineResult into a structured input the LLM can consume."""
    rationales_block = "\n".join(f"- {r}" for r in engine_result.rationales)

    return (
        f"ESI Level: {engine_result.esi_level}\n"
        f"Decision path: {engine_result.decision_path}\n"
        f"Rules that fired: {', '.join(engine_result.rules_fired)}\n\n"
        f"Clinical rationales (you MAY translate but MAY NOT add to these):\n"
        f"{rationales_block}"
    )


def generate_explanation(engine_result: EngineResult) -> str:
    """
    Call the LLM to produce a patient-facing explanation message.

    Temperature is slightly nonzero here (0.3) to allow natural phrasing
    variation. The medical content is fixed — only the wording flexes.
    """
    llm = get_llm(temperature=0.3)

    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", build_user_message(engine_result)),
        ]
    )

    # response is an AIMessage; the actual text is in .content
    return response.content