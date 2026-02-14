from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


DEFAULT_PRICING: dict[str, Any] = {
    "currency": "USD",
    "source": "https://docs.x.ai/developers/models",
    "models": {
        "grok-imagine-video": {
            "per_second": {
                "480p": 0.05,
                "720p": 0.05,
            }
        }
    },
    "violation_fee": 0.05,
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@dataclass
class PricingStore:
    path: Path
    data: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_PRICING))
    last_loaded: str = field(default_factory=utc_now)

    def refresh(self) -> dict[str, Any]:
        if self.path.exists():
            loaded = json.loads(self.path.read_text())
        else:
            loaded = {}
        self.data = _deep_merge(DEFAULT_PRICING, loaded)
        self.last_loaded = utc_now()
        return self.data

    def to_dict(self) -> dict[str, Any]:
        return {
            "pricing": self.data,
            "last_loaded": self.last_loaded,
        }

    @property
    def currency(self) -> str:
        return str(self.data.get("currency", "USD"))

    @property
    def violation_fee(self) -> float:
        return float(self.data.get("violation_fee", DEFAULT_PRICING["violation_fee"]))

    def get_video_rate(self, resolution: str) -> float:
        model = self.data.get("models", {}).get("grok-imagine-video", {})
        per_second = model.get("per_second", {})
        rate = per_second.get(resolution)
        if rate is None:
            rate = DEFAULT_PRICING["models"]["grok-imagine-video"]["per_second"].get(resolution, 0.05)
        return float(rate)

    def estimate_video_cost(self, duration: int, resolution: str) -> float:
        return round(self.get_video_rate(resolution) * duration, 4)
