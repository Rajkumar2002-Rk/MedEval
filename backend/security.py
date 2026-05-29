"""
API key authentication.

Single shared API key model (Phase 1). Clients send the key in the
X-API-Key request header. The dependency `verify_api_key` is attached to
any endpoint that requires authentication.

"""

import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status


load_dotenv()


API_KEY = os.environ.get("MEDEVAL_API_KEY")
API_KEY_HEADER_NAME = "X-API-Key"


def verify_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER_NAME)) -> None:
    if API_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfigured: MEDEVAL_API_KEY missing from environment.",
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )