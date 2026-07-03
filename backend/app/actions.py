from typing import Optional


def _dollars(value: Optional[float]) -> str:
    if value is None:
        return "$0"
    return f"${value:,.0f}"


def draft_action(decision: dict, metric: dict) -> dict:
    action = decision.get("decision", "watch")
    daily = metric.get("est_daily_spend") or 0.0
    platform = metric.get("platform")
    campaign = metric.get("campaign")
    ad_set = metric.get("ad_set")

    base_payload = {
        "platform": platform,
        "campaign": campaign,
        "ad_set": ad_set,
        "match_by": "name",
    }

    if action == "kill":
        text = f"Pause — cut daily budget from {_dollars(daily)} to $0."
        payload = {**base_payload, "action": "pause", "params": {"daily_budget": 0}}
    elif action == "scale":
        new_daily = round((daily or 0) * 1.5)
        if new_daily <= 0:
            text = "Scale — increase daily budget by ~50%."
            payload = {**base_payload, "action": "increase_budget", "params": {"pct": 50}}
        else:
            text = f"Scale — raise daily budget from {_dollars(daily)} to {_dollars(new_daily)}."
            payload = {**base_payload, "action": "set_budget", "params": {"daily_budget": new_daily}}
    else:
        text = "Hold — no budget change; re-check in 24–48h."
        payload = {**base_payload, "action": "none", "params": {}}

    return {"drafted_action": text, "mcp_payload": payload}


def build_summary(metrics: list[dict], decisions: list[dict]) -> dict:
    by_key = {
        (m["platform"], m["campaign"], m["ad_set"]): m for m in metrics
    }
    counts = {"scale": 0, "kill": 0, "watch": 0}
    wasted = 0.0
    for decision in decisions:
        action = decision.get("decision", "watch")
        counts[action] = counts.get(action, 0) + 1
        if action == "kill":
            key = (decision["platform"], decision["campaign"], decision["ad_set"])
            metric = by_key.get(key)
            if metric:
                wasted += metric.get("est_daily_spend") or 0.0

    total_daily = sum((m.get("est_daily_spend") or 0.0) for m in metrics)
    platforms = len({m["platform"] for m in metrics})

    return {
        "entities": len(metrics),
        "platforms": platforms,
        "scale": counts["scale"],
        "kill": counts["kill"],
        "watch": counts["watch"],
        "wasted_daily_spend": round(wasted, 2),
        "total_daily_spend": round(total_daily, 2),
    }
