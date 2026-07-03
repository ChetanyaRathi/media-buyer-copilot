import io
from typing import Optional

import pandas as pd

from . import agent
from .config import get_settings
from .schema import CANONICAL_FIELDS

ALIASES = {
    "campaign": ["campaign name", "campaign", "campaign_name"],
    "ad_set": ["ad set name", "ad group name", "adgroup name", "ad set", "adset", "ad group", "adgroup"],
    "date": ["reporting starts", "day", "date", "reporting date"],
    "spend": ["amount spent", "amount spent (usd)", "cost", "spend", "total spent", "amount"],
    "revenue": ["conversion value", "conversions value", "purchase value", "total revenue", "revenue", "sales", "purchases conversion value"],
    "conversions": ["results", "conversions", "conversion", "leads", "purchases", "total conversions"],
    "clicks": ["link clicks", "clicks", "clicks (all)", "click"],
    "impressions": ["impressions", "impression", "impr"],
}

PLATFORM_HINTS = {
    "meta": ["meta", "facebook", "fb", "instagram"],
    "google": ["google", "gads", "adwords"],
    "tiktok": ["tiktok", "tt"],
    "taboola": ["taboola", "tab"],
}


def load_dataframe(content: bytes, filename: str) -> pd.DataFrame:
    name = (filename or "").lower()
    try:
        if name.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(content))
        return pd.read_csv(io.BytesIO(content))
    except Exception as error:
        raise ValueError(f"Could not read '{filename}'. Upload a valid CSV or XLSX export ({error}).")


def detect_platform(filename: str, columns) -> str:
    name = (filename or "").lower()
    for platform, hints in PLATFORM_HINTS.items():
        if any(hint in name for hint in hints):
            return platform
    return "unknown"


def _norm(value: str) -> str:
    return str(value).strip().lower()


def map_columns(df: pd.DataFrame, platform_hint: str) -> dict:
    columns = list(df.columns)
    normalized = {_norm(column): column for column in columns}
    used: set[str] = set()
    mapping: dict[str, str] = {}

    for field in ["campaign", "ad_set", "date", "spend", "revenue", "conversions", "clicks", "impressions"]:
        for alias in ALIASES[field]:
            match = None
            for norm_name, original in normalized.items():
                if original in used:
                    continue
                if norm_name == alias or norm_name.startswith(alias) or alias in norm_name:
                    match = original
                    break
            if match:
                mapping[field] = match
                used.add(match)
                break

    unmapped = [f for f in ALIASES if f not in mapping]
    settings = get_settings()
    if unmapped and settings.llm_enabled:
        remaining = [column for column in columns if column not in used]
        if remaining:
            samples = df.head(3).to_dict(orient="records")
            try:
                additions = agent.llm_map_columns(unmapped, remaining, samples)
                for field, column in additions.items():
                    if field in CANONICAL_FIELDS and column in columns and column not in used:
                        mapping[field] = column
                        used.add(column)
            except Exception:
                pass

    if "spend" not in mapping:
        raise ValueError(
            "Could not find a spend/cost column in this export. "
            f"Columns seen: {', '.join(map(str, columns))}."
        )

    return mapping


def _to_number(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(r"[$,%]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def to_canonical(df: pd.DataFrame, mapping: dict, platform: str) -> list[dict]:
    result = pd.DataFrame()
    result["platform"] = [platform] * len(df)

    for field in ["campaign", "ad_set"]:
        if field in mapping:
            result[field] = df[mapping[field]].astype(str).fillna("unknown")
        else:
            result[field] = "unknown"

    if "date" in mapping:
        parsed = pd.to_datetime(df[mapping["date"]], errors="coerce")
        result["date"] = parsed.dt.date.astype(str).where(parsed.notna(), None)
    else:
        result["date"] = None

    for field in ["spend", "impressions", "clicks", "conversions", "revenue"]:
        if field in mapping:
            result[field] = _to_number(df[mapping[field]])
        else:
            result[field] = 0.0

    return result.to_dict(orient="records")
