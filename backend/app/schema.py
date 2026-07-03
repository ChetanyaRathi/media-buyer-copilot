from enum import Enum
from typing import Optional

from pydantic import BaseModel

CANONICAL_FIELDS = [
    "platform",
    "campaign",
    "ad_set",
    "date",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue",
]

REQUIRED_FIELDS = ["spend"]


class Decision(str, Enum):
    SCALE = "scale"
    KILL = "kill"
    WATCH = "watch"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MetricRow(BaseModel):
    platform: str
    campaign: str
    ad_set: str
    days: int
    spend: float
    impressions: int
    clicks: int
    conversions: float
    revenue: float
    est_daily_spend: float
    roas: Optional[float] = None
    cpa: Optional[float] = None
    cpl: Optional[float] = None
    epc: Optional[float] = None
    ctr: Optional[float] = None
    cvr: Optional[float] = None
    roas_trend_pct: Optional[float] = None


class DecisionRow(BaseModel):
    platform: str
    campaign: str
    ad_set: str
    decision: Decision
    confidence: Confidence
    reasoning: str
    verified: bool = True
    critique_note: Optional[str] = None
    drafted_action: Optional[str] = None
    mcp_payload: Optional[dict] = None


class Summary(BaseModel):
    entities: int
    platforms: int
    scale: int
    kill: int
    watch: int
    wasted_daily_spend: float
    total_daily_spend: float


class AnalysisResult(BaseModel):
    summary: Summary
    metrics: list[MetricRow]
    decisions: list[DecisionRow]


class ChatRequest(BaseModel):
    question: str
    context: dict


class ChatResponse(BaseModel):
    answer: str
