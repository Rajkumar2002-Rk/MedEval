import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"

def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """
    Return a configured chat model.

    Args:
        temperature: 0.0 = deterministic (recommended for medical extraction);
                     higher values introduce variability (acceptable for the
                     patient-facing explanation text where some natural phrasing
                     helps readability).

    Raises:
        RuntimeError: if OPENAI_API_KEY is missing from the environment.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found. Make sure backend/.env exists and contains a valid OpenAI API key.")
    
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=temperature,
    )

