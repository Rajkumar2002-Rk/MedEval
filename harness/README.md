# medeval-harness

Evaluation harness for the [MedEval](https://github.com/Rajkumar2002-Rk/MedEval) triage agent.

Scores a running MedEval agent against a 50-case ESI dataset on:

- Exact and adjacent ESI level accuracy
- Under-triage and over-triage rates (the safety metrics)
- Hallucination rate (LLM-extracted facts unsupported by complaint text)
- Decision-path consistency
- Cost per case and per-evaluation
- Latency (p50 / p95)

## Install

```bash
pip install medeval-harness