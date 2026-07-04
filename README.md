# media-buyer-copilot

AI co-pilot for media buyers — turns cross-platform ad spend into grounded **scale / kill / watch** decisions, with the reasoning behind each call.


**Stack:** FastAPI · LangGraph · React (Vite) · runs fully local on Ollama (Mistral 7B), or Gemini with one env var

Drop in a raw ad export (Meta, Google, TikTok, Taboola — the messy CSV/XLSX you already download). The tool normalizes it, computes the metrics that matter, and an LLM pipeline recommends what to scale, kill, and watch — then critiques its own recommendations before showing them. Every call is backed by the numbers and a one-line rationale you can click into. No API keys, no billing: it runs on a local model out of the box.

---

## What it does

You give it yesterday's numbers; it gives you a morning brief. For every ad set across every platform it decides:

- **Scale** — profitable and stable or improving, worth more budget.
- **Kill** — losing money with real spend behind it, or falling fast.
- **Watch** — borderline or too little data to call yet.

Each recommendation comes with the metrics that drove it (ROAS, CPA/CPL, EPC, CTR, CVR, trend), a plain-English rationale, a confidence level, and a drafted budget move with an MCP-ready payload. There's a chat box to interrogate the results — "why kill the lookalike?", "what if I 2x the winners?" — answered strictly from the analyzed data.

## Why I built this one

The brief was to build anything valuable to the media-buying team. The projects already in flight — creative generation, an MCP ad uploader, a landing-page CMS — are all about *producing and shipping* ads. None of them touch the decision that actually moves the P&L every single morning: given yesterday's numbers across every platform, where does the next dollar go?

That call is made by hand, in spreadsheets, under time pressure — and it's exactly where money quietly leaks. So I built the co-pilot for that gap instead of rebuilding something the team already owns.

It's deliberately **assistive, not autonomous**: it recommends and shows its math, the buyer decides. Optimization is where a buyer's judgment and instinct live — a tool that overrides that gets ignored; one that makes the reasoning fast and legible gets used.

## What I'd build next full-time

- **Close the loop.** The drafted budget moves already carry MCP-shaped payloads — wire them to the real platform APIs so a click executes the change.
- **Scheduled pulls, not uploads.** Ingest on a cron and deliver the brief to the inbox each morning.
- **Account-aware targets.** Learn each account's target ROAS / CPA instead of reasoning relatively, and track recommendation to outcome to measure whether the calls were right.
- **Fine-tune a small local model.** With labeled buyer decisions, fine-tune an open 7B model on this exact task so it runs fully local, cheap, and sharp at scale.
- **Deeper cuts.** Creative- and audience-level breakdowns, pacing / budget-cap awareness, and anomaly alerts when a winner suddenly turns.

## How it works

Guiding principle: **the LLM reasons, the code does the arithmetic.** Metrics are never hallucinated — they're computed in pandas. The model only classifies and explains, and two guardrails keep it honest: a second LLM pass that checks its work, and a deterministic sanity clamp.

LangGraph pipeline: `ingest -> metrics -> decide -> critique -> actions`

- **ingest** — parse CSV/XLSX and map arbitrary column names to a canonical schema. A deterministic alias table handles the common exports; the LLM fills any gaps it doesn't recognize.
- **metrics** — deterministic pandas: spend, ROAS, CPA/CPL, EPC, CTR, CVR, and day-over-day trend, aggregated per ad set.
- **decide** — the model classifies each ad set scale / kill / watch with a confidence and a rationale, grounded only in the computed numbers.
- **critique** — a verifier pass confirms each call is actually supported by the data, flags anything unsupported, and downgrades confidence when the signal is thin.
- **sanity clamp** — a deterministic rule the model cannot override: a sub-1.0 ROAS can never be "scale," and a marginal 1.0-1.5 ROAS is held at "watch." This is why the decisions stay trustworthy even on a small local model.

If the LLM is unavailable, the pipeline still runs end to end on a rule-based fallback, so it never hard-fails.

**Local-first and provider-agnostic.** Every model call lives in one file (`app/agent.py`) behind a single switch. It ships pointing at a local Ollama model (Mistral 7B) so it runs with no API key and no billing. Set `LLM_PROVIDER=gemini` and add a key to route the exact same pipeline through Gemini instead.

## Run it locally

**Prereqs:** Python 3.10+, Node 18+, and [Ollama](https://ollama.com). Pull the local model once:
```
ollama pull mistral
```

**Backend**
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```
`.env` defaults to Ollama + Mistral, so there's nothing to configure. To use Gemini instead, set `LLM_PROVIDER=gemini` and add your `GEMINI_API_KEY` in `backend/.env`.

**Frontend**
```
cd frontend
npm install
cp .env.example .env
npm run dev
```
`VITE_API_URL` defaults to `http://localhost:8000`. Open the dev URL and click **Try it with sample data**, or drop your own export. (First analysis on a local model takes a few seconds while the model loads.)

## Evaluation

A small labeled set checks decision accuracy and confirms the guardrails catch a planted bad call:
```
cd backend
python eval/run_eval.py
```
Decision accuracy on the labeled set: **100% (6/6)**. The self-critique + clamp also caught a deliberately planted false "scale" on a losing ad set and corrected it to "kill."

## Notes

- **Runs fully local, no keys.** Provider-agnostic: a local Ollama model (Mistral 7B) by default, or Gemini with one env var. No OAuth, no ad-platform keys, no billing — it works the moment you clone it.
- **Real exports first.** The normalizer is built to eat the actual files buyers download, odd headers and all. Sample data is a fallback, not the main path.
- **Grounded, not vibes.** Every number shown is computed in code; the model's job is judgment and explanation, checked by the critique pass and a hard sanity clamp — which is what lets a modest 7B local model produce trustworthy calls.
