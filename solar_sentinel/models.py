from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass(slots=True)
class SpaceWeather:
    kp_index: float
    solar_wind_kms: float
    xray_flux: str
    proton_flux: str = "quiet"


@dataclass(slots=True)
class CosmicState:
    moon_phase: str
    lunar_illumination: float
    tide_range_m: float
    tide_slope: float
    solar_rotation_phase: str = ""


@dataclass(slots=True)
class MarketState:
    btc_price: float
    weekly_return_pct: float
    ml_confidence_pct: float
    breakout_probability_pct: float
    vol_risk_pct: float
    market_compression_score: float
    posture: str = "WAIT"
    data_quality_guard: bool = False


@dataclass(slots=True)
class ForecastPoint:
    date: date
    price: float


@dataclass(slots=True)
class Snapshot:
    market: MarketState
    space: SpaceWeather
    cosmic: CosmicState
    forecast: List[ForecastPoint] = field(default_factory=list)
    cvi: float = 0.0
    energy_score: float = 0.0
    regime: str = "RANGE"
    trade_signal: str = "WAIT"
    notes: List[str] = field(default_factory=list)
    breakout_long_above: float | None = None
    momentum_short_below: float | None = None
    prime_trade_days: List[str] = field(default_factory=list)
