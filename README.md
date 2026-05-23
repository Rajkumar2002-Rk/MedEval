# MedEval

A healthcare AI triage assistant that uses deterministic Python rules to decide urgency level, and an LLM only to explain the decision in plain English. Built to eliminate hallucination risk where it matters most: safety-critical medical decisions.

## Status

🚧 Phase 1 in progress — LangGraph triage agent + FastAPI backend + React frontend.

## Architecture

- **Phase 1** — LangGraph triage agent, FastAPI backend, React frontend (patient + doctor UI), API key auth, Langfuse observability, Docker, deployed on AWS EC2.
- **Phase 2** — Evaluation harness scoring the agent on safety, hallucination, and accuracy against a 50-case ESI dataset. Runs in CI. Published as `medeval-harness` on PyPI.
- **Phase 3** — Multi-provider LLM router (Claude, GPT, Gemini) with a cost dashboard. Deterministic rules published as `triage-rules` on PyPI.

## Tech Stack

- **Backend** — Python, FastAPI, LangGraph
- **Frontend** — React
- **LLM** — Anthropic Claude (Phase 1), plus OpenAI and Google (Phase 3)
- **Observability** — Langfuse
- **Deployment** — Docker, AWS EC2

## Repository Layout
- backend/ FastAPI + LangGraph agent
- frontend/ React UI (patient + doctor)
- harness/ Phase 2 — evaluation harness
- router/ Phase 3 — multi-provider LLM router
- data/ ESI dataset (50 cases)
- docs/ Notes and references


## Disclaimer

This is a portfolio project. It is **not** a medical device and must not be used for real clinical decisions.