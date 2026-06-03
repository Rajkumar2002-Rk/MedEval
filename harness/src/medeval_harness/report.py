from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

from medeval_harness.scorer import EvaluationSummary


def print_report(summary: EvaluationSummary, console: Console | None = None) -> None:
    console = console or Console()

    # Headline metrics table
    metrics = Table(title="MedEval Evaluation — Summary", title_style="bold")
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Value", justify="right")

    metrics.add_row("Total cases", str(summary.total_cases))
    metrics.add_row("Completed", str(summary.completed_cases))
    metrics.add_row("Errors", str(summary.error_count))
    metrics.add_row("Exact accuracy", f"{summary.exact_accuracy}%")
    metrics.add_row("Tolerant accuracy", f"{summary.tolerant_accuracy}%")
    metrics.add_row(
        "[bold]Under-triage rate[/bold]",
        f"[bold red]{summary.under_triage_rate}%[/bold red]",
    )
    metrics.add_row("Over-triage rate", f"{summary.over_triage_rate}%")
    metrics.add_row("Path match rate", f"{summary.path_match_rate}%")
    metrics.add_row("Latency p50", f"{summary.latency_p50}s")
    metrics.add_row("Latency p95", f"{summary.latency_p95}s")
    console.print(metrics)

    # Misses table
    misses = [c for c in summary.per_case if not c.within_tolerance]
    if misses:
        mt = Table(title="Misses (outside tolerance)", title_style="bold yellow")
        mt.add_column("Case", style="cyan")
        mt.add_column("Expected", justify="center")
        mt.add_column("Got", justify="center")
        mt.add_column("Direction")
        for c in misses:
            color = "red" if c.triage_direction == "under" else "yellow"
            got = str(c.predicted_level) if c.predicted_level is not None else "ERR"
            mt.add_row(
                c.case_id,
                str(c.expected_level),
                got,
                f"[{color}]{c.triage_direction.upper()}[/{color}]",
            )
        console.print(mt)
    else:
        console.print("[bold green]No misses outside tolerance![/bold green]")


def save_report(summary: EvaluationSummary, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_cases": summary.total_cases,
            "completed_cases": summary.completed_cases,
            "error_count": summary.error_count,
            "exact_accuracy": summary.exact_accuracy,
            "tolerant_accuracy": summary.tolerant_accuracy,
            "under_triage_rate": summary.under_triage_rate,
            "over_triage_rate": summary.over_triage_rate,
            "path_match_rate": summary.path_match_rate,
            "latency_p50": summary.latency_p50,
            "latency_p95": summary.latency_p95,
        },
        "per_case": [c.model_dump() for c in summary.per_case],
    }

    path.write_text(json.dumps(payload, indent=2))
    return path