from typing import Optional

import pandas as pd


def _safe_div(numerator: float, denominator: float) -> Optional[float]:
    if denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _round(value: Optional[float], digits: int = 2) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def _roas_trend(group: pd.DataFrame) -> Optional[float]:
    if "date" not in group.columns:
        return None
    dated = group.dropna(subset=["date"])
    if dated["date"].nunique() < 2:
        return None
    daily = (
        dated.groupby("date")[["spend", "revenue"]].sum().sort_index()
    )
    daily = daily[daily["spend"] > 0]
    if len(daily) < 2:
        return None
    daily_roas = daily["revenue"] / daily["spend"]
    first, last = daily_roas.iloc[0], daily_roas.iloc[-1]
    if first == 0:
        return None
    return round(((last - first) / first) * 100, 1)


def compute_metrics(rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    df = pd.DataFrame(rows)
    for column in ["spend", "impressions", "clicks", "conversions", "revenue"]:
        if column not in df.columns:
            df[column] = 0.0
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for column in ["platform", "campaign", "ad_set"]:
        if column not in df.columns:
            df[column] = "unknown"
        df[column] = df[column].fillna("unknown").astype(str)

    keys = ["platform", "campaign", "ad_set"]
    metrics: list[dict] = []

    for (platform, campaign, ad_set), group in df.groupby(keys):
        spend = float(group["spend"].sum())
        impressions = int(group["impressions"].sum())
        clicks = int(group["clicks"].sum())
        conversions = float(group["conversions"].sum())
        revenue = float(group["revenue"].sum())

        days = 1
        if "date" in group.columns:
            distinct = group["date"].dropna().nunique()
            days = int(distinct) if distinct > 0 else 1

        row = {
            "platform": platform,
            "campaign": campaign,
            "ad_set": ad_set,
            "days": days,
            "spend": _round(spend),
            "impressions": impressions,
            "clicks": clicks,
            "conversions": _round(conversions),
            "revenue": _round(revenue),
            "est_daily_spend": _round(spend / days if days else spend),
            "roas": _round(_safe_div(revenue, spend)),
            "cpa": _round(_safe_div(spend, conversions)),
            "cpl": _round(_safe_div(spend, conversions)),
            "epc": _round(_safe_div(revenue, clicks)),
            "ctr": _round(_safe_div(clicks * 100.0, impressions)),
            "cvr": _round(_safe_div(conversions * 100.0, clicks)),
            "roas_trend_pct": _roas_trend(group),
        }
        metrics.append(row)

    metrics.sort(key=lambda item: item["spend"] or 0, reverse=True)
    return metrics
