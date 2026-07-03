FIXTURES = [
    {"platform": "meta", "campaign": "Skincare", "ad_set": "Broad Winner", "days": 4,
     "spend": 1260, "clicks": 3760, "est_daily_spend": 315, "roas": 2.52, "cpa": 4.85,
     "epc": 0.84, "ctr": 2.3, "cvr": 6.9, "roas_trend_pct": 6.0, "label": "scale"},
    {"platform": "tiktok", "campaign": "Launch", "ad_set": "UGC Hook A", "days": 3,
     "spend": 615, "clicks": 2430, "est_daily_spend": 205, "roas": 2.34, "cpa": 5.0,
     "epc": 0.59, "ctr": 1.3, "cvr": 5.1, "roas_trend_pct": 2.0, "label": "scale"},
    {"platform": "meta", "campaign": "Skincare", "ad_set": "Lookalike Loser", "days": 4,
     "spend": 1025, "clicks": 2400, "est_daily_spend": 256, "roas": 0.52, "cpa": 18.3,
     "epc": 0.22, "ctr": 2.0, "cvr": 2.4, "roas_trend_pct": -51.0, "label": "kill"},
    {"platform": "tiktok", "campaign": "Launch", "ad_set": "Discount Angle", "days": 3,
     "spend": 555, "clicks": 1530, "est_daily_spend": 185, "roas": 0.56, "cpa": 22.2,
     "epc": 0.20, "ctr": 1.0, "cvr": 1.6, "roas_trend_pct": -30.0, "label": "kill"},
    {"platform": "meta", "campaign": "Skincare", "ad_set": "Retarget Borderline", "days": 4,
     "spend": 480, "clicks": 1200, "est_daily_spend": 120, "roas": 1.22, "cpa": 9.1,
     "epc": 0.49, "ctr": 2.0, "cvr": 4.4, "roas_trend_pct": 0.0, "label": "watch"},
    {"platform": "google", "campaign": "Search", "ad_set": "New Exact", "days": 1,
     "spend": 8, "clicks": 12, "est_daily_spend": 8, "roas": 1.4, "cpa": 4.0,
     "epc": 0.93, "ctr": 3.0, "cvr": 16.7, "roas_trend_pct": None, "label": "watch"},
]

WRONG_DECISION = {
    "platform": "tiktok", "campaign": "Launch", "ad_set": "Discount Angle",
    "decision": "scale", "confidence": "high",
    "reasoning": "Strong ROAS of 3.1 with an improving trend, worth scaling aggressively.",
}
