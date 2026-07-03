import json
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import get_settings

VALID_DECISIONS = {"scale", "kill", "watch"}
VALID_CONFIDENCE = {"high", "medium", "low"}

DECISION_SYSTEM = """You are a senior media-buying analyst at an affiliate marketing company. \
You review performance data across Meta, Google, TikTok, and Taboola and decide where money should move.

For each ad set, output exactly one decision:
- "scale": profitable and stable or improving, with meaningful volume. Strong ROAS (roughly >= 1.5) or a healthy cost per conversion, and a flat or positive trend.
- "kill": clearly unprofitable with meaningful spend (ROAS well below 1.0 or cost per conversion far too high), or sharply declining while still burning budget.
- "watch": borderline, mixed signals, or too little spend/clicks to judge confidently.

Rules:
- Base every judgment ONLY on the numbers provided. Never invent a metric.
- If revenue is zero or missing, judge on cost per conversion (cpa/cpl), CTR, and CVR instead of ROAS.
- You are assistive: you recommend and explain, the human decides.
- Keep each reasoning to one or two sentences and cite the specific metrics that drove the call.

Return ONLY a JSON array, no prose, no code fences. Each item:
{"platform": str, "campaign": str, "ad_set": str, "decision": "scale|kill|watch", "confidence": "high|medium|low", "reasoning": str}"""

CRITIQUE_SYSTEM = """You are a verifier checking another analyst's recommendations against the raw metrics. \
For each proposed decision, confirm it is actually supported by the numbers provided.

Checks:
- Does the reasoning cite only metrics present in the data? If it references a number that is not in the data, mark it unverified and note why.
- Is the decision consistent with the metrics and the scale/kill/watch rubric? If not, correct it.
- Is the confidence appropriate for how strong the signal is? Downgrade it if the data is thin.

Do not introduce new numbers. Return ONLY a JSON array, no prose, no code fences. Each item:
{"platform": str, "campaign": str, "ad_set": str, "decision": "scale|kill|watch", "confidence": "high|medium|low", "reasoning": str, "verified": true|false, "critique_note": str or null}"""

CHAT_SYSTEM = """You are a media-buying co-pilot. Answer the user's question using ONLY the analysis data provided \
(summary, decisions, and metrics). Be concise and specific, cite the relevant numbers, and never invent data. \
If the answer is not in the data, say so."""

METRIC_KEYS = [
    "platform", "campaign", "ad_set", "spend", "est_daily_spend", "days",
    "clicks", "roas", "cpa", "epc", "ctr", "cvr", "roas_trend_pct",
]


def _llm(temperature: float = 0.2):
    settings = get_settings()
    if settings.provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=settings.model, temperature=temperature)
    return ChatGoogleGenerativeAI(model=settings.model, temperature=temperature)


def _parse_json(text: str):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
        raise


def _slim(metrics: list[dict]) -> list[dict]:
    return [{key: row.get(key) for key in METRIC_KEYS} for row in metrics]


def _normalize_decision(item: dict) -> Optional[dict]:
    decision = str(item.get("decision", "")).strip().lower()
    confidence = str(item.get("confidence", "medium")).strip().lower()
    if decision not in VALID_DECISIONS:
        return None
    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"
    return {
        "platform": str(item.get("platform", "unknown")),
        "campaign": str(item.get("campaign", "unknown")),
        "ad_set": str(item.get("ad_set", "unknown")),
        "decision": decision,
        "confidence": confidence,
        "reasoning": str(item.get("reasoning", "")).strip(),
        "verified": bool(item.get("verified", True)),
        "critique_note": item.get("critique_note"),
    }


def _rule_based(metric: dict) -> dict:
    daily = metric.get("est_daily_spend") or 0.0
    clicks = metric.get("clicks") or 0
    roas = metric.get("roas")
    trend = metric.get("roas_trend_pct")

    if daily < 20 or clicks < 20:
        decision, confidence = "watch", "low"
        reasoning = f"Only {clicks} clicks on ~${daily:,.0f}/day — too little data to judge."
    elif roas is not None and roas >= 1.5 and (trend is None or trend >= -10):
        decision, confidence = "scale", "medium"
        reasoning = f"ROAS {roas} on ~${daily:,.0f}/day with a stable trend."
    elif roas is not None and roas < 1.0:
        decision, confidence = "kill", "medium"
        reasoning = f"ROAS {roas} on ~${daily:,.0f}/day is unprofitable."
    else:
        decision, confidence = "watch", "low"
        reasoning = "Mixed signals; hold and gather more data."

    return {
        "platform": metric["platform"],
        "campaign": metric["campaign"],
        "ad_set": metric["ad_set"],
        "decision": decision,
        "confidence": confidence,
        "reasoning": reasoning,
        "verified": True,
        "critique_note": None,
    }


def _sanity_clamp(decision: dict, metric: dict) -> dict:
    roas = metric.get("roas")
    if roas is None:
        return decision
    call = decision.get("decision")
    if roas < 1.0 and call == "scale":
        decision["decision"] = "kill"
        decision["confidence"] = "high"
        decision["critique_note"] = f"Overridden: ROAS {roas} is below break-even, cannot scale."
    elif 1.0 <= roas < 1.5 and call == "scale":
        decision["decision"] = "watch"
        decision["confidence"] = "medium"
        decision["critique_note"] = f"Overridden: ROAS {roas} is marginal, hold rather than scale."
    return decision


def _fill_missing(metrics: list[dict], decisions: list[dict]) -> list[dict]:
    by_key = {(d["platform"], d["campaign"], d["ad_set"]): d for d in decisions}
    complete = []
    for metric in metrics:
        key = (metric["platform"], metric["campaign"], metric["ad_set"])
        complete.append(by_key.get(key) or _rule_based(metric))
    return complete


def llm_map_columns(fields: list[str], columns: list, sample_rows: list[dict]) -> dict:
    system = (
        "Map export columns to canonical fields. Return ONLY a JSON object whose keys are a subset of "
        f"{fields} and whose values are exact column names from this list: {list(columns)}. "
        "Only include a field if a column clearly matches it. No code fences."
    )
    user = f"Columns: {list(columns)}\nSample rows: {json.dumps(sample_rows, default=str)[:1500]}"
    response = _llm(temperature=0.0).invoke([SystemMessage(content=system), HumanMessage(content=user)])
    result = _parse_json(response.content)
    return result if isinstance(result, dict) else {}


def decide(metrics: list[dict]) -> list[dict]:
    if not metrics:
        return []
    settings = get_settings()
    if not settings.llm_enabled:
        return [_rule_based(metric) for metric in metrics]

    user = json.dumps(_slim(metrics), default=str)
    try:
        response = _llm(temperature=0.2).invoke(
            [SystemMessage(content=DECISION_SYSTEM), HumanMessage(content=user)]
        )
        raw = _parse_json(response.content)
        parsed = [d for d in (_normalize_decision(item) for item in raw) if d]
    except Exception:
        parsed = []
    return _fill_missing(metrics, parsed)


def critique(metrics: list[dict], decisions: list[dict]) -> list[dict]:
    if not decisions:
        return []
    settings = get_settings()
    if not settings.llm_enabled:
        return decisions

    payload = {"metrics": _slim(metrics), "decisions": decisions}
    user = json.dumps(payload, default=str)
    try:
        response = _llm(temperature=0.0).invoke(
            [SystemMessage(content=CRITIQUE_SYSTEM), HumanMessage(content=user)]
        )
        raw = _parse_json(response.content)
        revised = [d for d in (_normalize_decision(item) for item in raw) if d]
        if revised:
            filled = _fill_missing(metrics, revised)
            by_key = {(m["platform"], m["campaign"], m["ad_set"]): m for m in metrics}
            return [_sanity_clamp(d, by_key.get((d["platform"], d["campaign"], d["ad_set"]), {})) for d in filled]
    except Exception:
        pass
    return decisions


def chat(question: str, context: dict) -> str:
    settings = get_settings()
    if not settings.llm_enabled:
        return "The LLM is not enabled. Set LLM_PROVIDER=ollama (local) or add a Gemini API key, then restart."
    slim_context = {
        "summary": context.get("summary"),
        "decisions": context.get("decisions"),
        "metrics": _slim(context.get("metrics", [])),
    }
    user = f"Question: {question}\n\nAnalysis data:\n{json.dumps(slim_context, default=str)[:12000]}"
    try:
        response = _llm(temperature=0.3).invoke(
            [SystemMessage(content=CHAT_SYSTEM), HumanMessage(content=user)]
        )
        return response.content.strip()
    except Exception as error:
        return f"Could not generate an answer ({error})."
