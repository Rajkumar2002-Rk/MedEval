# MedEval

> Healthcare AI triage assistant where deterministic Python rules make the safety-critical decision and an LLM only writes the explanation. Built on the AHRQ ESI Handbook v4.

[![Phase 1](https://img.shields.io/badge/Phase_1-shipped-22c55e)]()
[![Phase 2](https://img.shields.io/badge/Phase_2-shipped-22c55e)]()
[![PyPI](https://img.shields.io/pypi/v/medeval-harness?label=medeval-harness&color=3775A9)](https://pypi.org/project/medeval-harness/)
[![CI](https://github.com/Rajkumar2002-Rk/MedEval/actions/workflows/eval.yml/badge.svg)](https://github.com/Rajkumar2002-Rk/MedEval/actions/workflows/eval.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)]()

---

## 🌐 Live Demo

**Try it:** [https://medeval.rajkumarai.dev](https://medeval.rajkumarai.dev) 🔒

> The demo is gated by an API key. Reach out if you'd like the key to try it.

![MedEval Patient View](docs/screenshot-patient.png)

---

## 🧠 The Key Idea

LLMs hallucinate. In healthcare, hallucinating an urgency level can kill someone.

So MedEval **structurally prevents** the LLM from making the urgency decision:

```
Patient complaint
       ↓
[ LLM ] extract structured facts from free text
       ↓
[ Python rules engine ] decide ESI level (1-5) ← LLM never sees this code
       ↓
[ LLM ] translate clinical rationale into plain English
       ↓
Patient-facing message
```

**The LLM cannot influence the safety-critical decision.** Every rule traces back to a specific page of the AHRQ ESI Implementation Handbook v4 — the protocol used by U.S. emergency departments.

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────────────────────┐
│  React + Vite   │ ───► │  FastAPI                         │
│  patient UI     │      │   ├─ /health                     │
│  doctor UI      │      │   └─ /triage (X-API-Key auth)    │
└─────────────────┘      │       │                          │
                         │       ▼                          │
                         │  LangGraph pipeline              │
                         │   ├─ extract  (OpenAI)           │
                         │   ├─ triage   (68 YAML rules)    │
                         │   └─ explain  (OpenAI)           │
                         │       │                          │
                         │       ▼                          │
                         │  Langfuse (traces every LLM call)│
                         └──────────────────────────────────┘
```

### Schema Highlights

- **`ExtractedFacts`** — 95-field Pydantic model. The LLM is constrained to produce only this shape via OpenAI structured output. Every field defaults to `False` (safe under-trigger > over-trigger).
- **`esi_rules.yaml`** — 68 rules across all four ESI decision points (A, B, C, D) plus pediatric overlays. Each rule cites its source page. Schema supports nested `any_of` / `all_of` and `applies_when` preconditions.
- **`engine.py`** — ~100 lines of pure Python. Loads YAML, evaluates rules in handbook order, returns level + rules fired + rationales + decision path.

---

## 🛠️ Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Lucide icons |
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| LLM orchestration | LangGraph, LangChain, OpenAI `gpt-4o-mini` (Anthropic planned) |
| Observability | Langfuse Cloud (per-call traces, latency, tokens) |
| Auth | API key in `X-API-Key` header |
| Containerization | Docker (multi-stage frontend build), Docker Compose |
| Deployment | AWS EC2 `t3.micro`, Ubuntu 24.04, Nginx reverse proxy, HTTPS via Let's Encrypt |
| Evaluation | `medeval-harness` (published on PyPI), GitHub Actions CI |

---

## 🚀 Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker Desktop (for containerized run)
- An OpenAI API key + Langfuse account

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in real keys
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### Or run the whole thing in Docker

```bash
docker compose up
```

---

## ☁️ Production Deploy (AWS EC2)

Images are published to Docker Hub:

```bash
docker pull raja1566/medeval-backend:latest
docker pull raja1566/medeval-frontend:latest
```

On the EC2 host:

```bash
docker compose up -d
```

In production, an **Nginx reverse proxy** on the host terminates TLS (Let's Encrypt,
auto-renewing) and routes traffic:

```
https://medeval.rajkumarai.dev/      → frontend container (:5173)
https://medeval.rajkumarai.dev/api/  → backend container  (:8000)
```

See [`docker-compose.yml`](docker-compose.yml) for the full configuration.

---

## 📁 Project Structure

```
MedEval/
├── backend/
│   ├── agent/                  LangGraph nodes + prompts
│   │   ├── prompts/
│   │   ├── llm.py              provider config (one place to swap)
│   │   ├── extraction.py       Node 1: complaint → facts
│   │   ├── explanation.py      Node 3: result → patient message
│   │   └── graph.py            LangGraph wiring
│   ├── rules/
│   │   ├── esi_rules.yaml      68 traceable rules
│   │   ├── facts.py            95-field ExtractedFacts contract
│   │   ├── result.py           EngineResult shape
│   │   └── engine.py           recursive evaluator
│   ├── main.py                 FastAPI app
│   ├── models.py               TriageRequest
│   ├── security.py             API key auth dependency
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api.ts              fetch wrapper + localStorage key mgmt
│   │   ├── types.ts            backend mirror
│   │   └── App.tsx             single-page UI
│   ├── nginx.conf
│   └── Dockerfile              multi-stage (Node build → Nginx)
├── harness/                    Phase 2 — evaluation harness (PyPI package)
│   ├── src/medeval_harness/
│   │   ├── cases.py            case schema + dataset loader
│   │   ├── runner.py           HTTP client that calls the agent
│   │   ├── scorer.py           safety-aware metrics (under/over-triage)
│   │   ├── report.py           rich terminal + JSON reports
│   │   ├── cli.py              `medeval-harness evaluate ...`
│   │   └── data/esi_cases.json 50 cases from the AHRQ handbook
│   └── pyproject.toml
├── .github/workflows/eval.yml  CI: auto-eval, fail-under threshold
├── docs/
│   └── esi-handbook-v4.pdf     source of truth
└── docker-compose.yml
```

---

## 🧪 Evaluation Harness (`medeval-harness`)

A standalone, **PyPI-published** package that scores the agent against a 50-case dataset
built from the worked examples in the AHRQ handbook (chapters 9–10, with official ESI answers).

```bash
pip install medeval-harness
medeval-harness evaluate --api-url https://medeval.rajkumarai.dev/api --api-key <key>
```

Unlike a generic accuracy benchmark, the harness reports **safety-aware metrics** — because
in triage, the direction of an error matters more than the rate:

| Metric | Baseline | After prompt tuning |
|---|---|---|
| Exact accuracy | 66% | 68% |
| **Under-triage rate** (marked *less* urgent than reality — dangerous) | **20%** | **10%** |
| Over-triage rate (marked *more* urgent — safe, wasteful) | 14% | 22% |

The tuning deliberately traded under-triage for over-triage — the *safe* direction in medicine.
Tuning was stopped at this point on purpose: pushing accuracy higher would have meant overfitting
the eval set. A proper held-out test set is noted as future work.

The harness runs in **GitHub Actions** on every change to the agent, rules, or dataset, and
**fails the build if exact accuracy drops below 60%** — catching triage regressions automatically.

---

## 🗺️ Roadmap

- **Phase 1** ✅ Live triage app (rules engine + LLM extraction + LLM explanation + UI + HTTPS deploy)
- **Phase 2** ✅ Evaluation harness — 50-case ESI dataset, safety-aware scoring, GitHub Actions CI, published as [`medeval-harness`](https://pypi.org/project/medeval-harness/) on PyPI
- **Phase 3** ⬜ Multi-provider LLM router (Claude, GPT, Gemini) with cost dashboard. Deterministic rules published as `triage-rules` on PyPI.

---

## ⚠️ Disclaimer

**MedEval is a portfolio project. It is NOT a medical device, has not been reviewed by any regulator, and must not be used for real clinical decisions.** All examples and screenshots use synthetic data.

---

## 📜 License

MIT — see [`LICENSE`](LICENSE) (forthcoming).

---

Built by [Rajkumar N](https://github.com/Rajkumar2002-Rk).