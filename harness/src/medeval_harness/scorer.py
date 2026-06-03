from __future__ import annotations

import statistics

from pydantic import BaseModel

from medeval_harness.runner import CaseResult


class CaseScore(BaseModel):
    case_id: str
    expected_level: int
    predicted_level: int | None
    within_tolerance: bool
    exact_match: bool
    triage_direction: str  
    path_match: bool
    latency_seconds: float
    error: str | None = None


class EvaluationSummary(BaseModel):
    total_cases: int
    completed_cases: int  
    error_count: int

    exact_accuracy: float
    tolerant_accuracy: float
    under_triage_rate: float
    over_triage_rate: float
    path_match_rate: float

    latency_p50: float
    latency_p95: float

    per_case: list[CaseScore]


def score_one(result: CaseResult) -> CaseScore:
    expected = result.case.expected.esi_level
    tolerance = result.case.expected.tolerance
    predicted = result.predicted_level

    if result.error is not None or predicted is None:
        return CaseScore(
            case_id=result.case.case_id,
            expected_level=expected,
            predicted_level=predicted,
            within_tolerance=False,
            exact_match=False,
            triage_direction="error",
            path_match=False,
            latency_seconds=result.latency_seconds,
            error=result.error or "no prediction returned",
        )

    exact = predicted == expected
    within_tol = abs(predicted - expected) <= tolerance

    if predicted == expected:
        direction = "exact"
    elif predicted > expected:
        direction = "under"  
    else:
        direction = "over"   

    path_match = result.predicted_path == result.case.expected.decision_path

    return CaseScore(
        case_id=result.case.case_id,
        expected_level=expected,
        predicted_level=predicted,
        within_tolerance=within_tol,
        exact_match=exact,
        triage_direction=direction,
        path_match=path_match,
        latency_seconds=result.latency_seconds,
    )


def score_all(results: list[CaseResult]) -> EvaluationSummary:
    scores = [score_one(r) for r in results]

    total = len(scores)
    completed = [s for s in scores if s.error is None]
    n_completed = len(completed)
    errors = total - n_completed

    def pct(count: int) -> float:
        return round(100 * count / n_completed, 1) if n_completed else 0.0

    exact_acc = pct(sum(1 for s in completed if s.exact_match))
    tolerant_acc = pct(sum(1 for s in completed if s.within_tolerance))
    under_rate = pct(sum(1 for s in completed if s.triage_direction == "under"))
    over_rate = pct(sum(1 for s in completed if s.triage_direction == "over"))
    path_rate = pct(sum(1 for s in completed if s.path_match))

    latencies = [s.latency_seconds for s in scores if s.latency_seconds > 0]
    p50 = round(statistics.median(latencies), 2) if latencies else 0.0
    p95 = (
        round(statistics.quantiles(latencies, n=20)[-1], 2)
        if len(latencies) >= 2
        else (round(latencies[0], 2) if latencies else 0.0)
    )

    return EvaluationSummary(
        total_cases=total,
        completed_cases=n_completed,
        error_count=errors,
        exact_accuracy=exact_acc,
        tolerant_accuracy=tolerant_acc,
        under_triage_rate=under_rate,
        over_triage_rate=over_rate,
        path_match_rate=path_rate,
        latency_p50=p50,
        latency_p95=p95,
        per_case=scores,
    )