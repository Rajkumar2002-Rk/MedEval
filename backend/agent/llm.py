import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler


load_dotenv()


DEFAULT_MODEL = "gpt-4o-mini"


langfuse_handler = CallbackHandler()


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. Make sure backend/.env exists and "
            "contains a valid OpenAI API key."
        )

    return ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=temperature,
        callbacks=[langfuse_handler],
    )