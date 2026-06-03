from __future__ import annotations

import os
import sys

import click
from rich.console import Console

from medeval_harness.cases import load_cases
from medeval_harness.runner import run_all
from medeval_harness.scorer import score_all
from medeval_harness.report import print_report, save_report


@click.group()
@click.version_option()
def main() -> None:
    """MedEval evaluation harness — score a triage agent on safety and accuracy."""


@main.command()
@click.option(
    "--api-url",
    required=True,
    help="Base URL of the running MedEval agent, e.g. http://127.0.0.1:8000",
)
@click.option(
    "--api-key",
    default=lambda: os.environ.get("MEDEVAL_API_KEY", ""),
    help="API key. Defaults to the MEDEVAL_API_KEY environment variable.",
)
@click.option(
    "--out",
    default=None,
    help="Optional path to write a JSON report (e.g. reports/baseline.json).",
)
@click.option(
    "--fail-under",
    type=float,
    default=None,
    help="Exit with code 1 if exact accuracy is below this percentage (for CI).",
)
def evaluate(api_url: str, api_key: str, out: str | None, fail_under: float | None) -> None:
    console = Console()

    if not api_key:
        console.print("[bold red]Error:[/bold red] no API key. Use --api-key or set MEDEVAL_API_KEY.")
        sys.exit(2)

    cases = load_cases()
    console.print(f"Loaded [bold]{len(cases)}[/bold] cases. Evaluating against {api_url} …\n")

    results = run_all(cases, api_url, api_key)
    summary = score_all(results)

    print_report(summary, console=console)

    if out:
        path = save_report(summary, out)
        console.print(f"\nReport written to [bold]{path}[/bold]")

    if fail_under is not None and summary.exact_accuracy < fail_under:
        console.print(
            f"\n[bold red]FAIL:[/bold red] accuracy {summary.exact_accuracy}% "
            f"is below threshold {fail_under}%."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()