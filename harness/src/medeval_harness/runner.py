from __future__ import annotations

import time

import httpx
from pydantic import BaseModel

from medeval_harness.cases import Case


class CaseResult(BaseModel):
    case: Case
    predicted_level: int | None = None
    predicted_path: str | None = None
    rules_fired: list[str] = []
    explanation: str | None = None
    latency_seconds: float = 0.0
    error: str | None = None


def run_case(
    client: httpx.Client,
    case: Case,
    api_url: str,
    api_key: str,
) -> CaseResult:
    payload = case.input.model_dump(exclude_none=True)

    start = time.perf_counter()
    try:
        response = client.post(
            f"{api_url}/triage",
            json=payload,
            headers={"X-API-Key": api_key},
            timeout=60.0,
        )
        latency = time.perf_counter() - start

        if response.status_code != 200:
            return CaseResult(
                case=case,
                latency_seconds=latency,
                error=f"HTTP {response.status_code}: {response.text[:200]}",
            )

        body = response.json()
        return CaseResult(
            case=case,
            predicted_level=body["esi_level"],
            predicted_path=body["decision_path"],
            rules_fired=body.get("rules_fired", []),
            explanation=body.get("explanation"),
            latency_seconds=latency,
        )

    except Exception as exc:  
        latency = time.perf_counter() - start
        return CaseResult(
            case=case,
            latency_seconds=latency,
            error=f"{type(exc).__name__}: {exc}",
        )


def run_all(
    cases: list[Case],
    api_url: str,
    api_key: str,
) -> list[CaseResult]:
    results: list[CaseResult] = []
    with httpx.Client() as client:
        for case in cases:
            result = run_case(client, case, api_url, api_key)
            results.append(result)
    return results