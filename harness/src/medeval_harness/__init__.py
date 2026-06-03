"""
medeval-harness — evaluation harness for the MedEval triage agent.

Runs a structured dataset of patient cases against a deployed agent,
scores accuracy, safety, hallucination, cost, and latency, and produces
a CI-friendly report.

Public API:
    from medeval_harness import run_evaluation, Case, EvaluationReport
"""

__version__ = "0.1.0"