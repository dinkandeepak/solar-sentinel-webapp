from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from typing import Iterable, List

from .models import CosmicState, ForecastPoint, MarketState, Snapshot, SpaceWeather


_XRAY_BASE = {
    "A": 0.0,
    "B": 0.10,
    "C": 0.25,
    "M": 0.65,
    "X": 1.00,
}


def _normalize_xray(xray_flux: str) -> float:
    text = (xray_flux or "").strip().upper()
    if not text:
        return 0.0

    band = text[0]
    base = _XRAY_BASE.get(band, 0.0)
    try:
        magnitude = float(text[1:]) if len(text) > 1 else 1.0
    except ValueError:
        magnitude = 1.0

    if band in {"A", "B", "C"}:
        return min(1.0, base + 0.02 * magnitude)
    if band == "M":
        return min(1.0, base + 0.03 * magnitude)
    if band == "X":
        return min(1.0, base + 0.05 * magnitude)
    return 0.0


def compute_cvi(kp_index: float, solar_wind_kms: float, xray_flux: str) -> float:
    """Cosmic Volatility Index: a compact volatility proxy from space weather."""
    kp_component = 0.5 * max(0.0, min(9.0, kp_index))
    wind_component = 0.3 * max(0.0, min(1.0, solar_wind_kms / 800.0))
    xray_component = 0.2 * _normalize_xray(xray_flux)
    return round(kp_component + wind_component + xray_component, 2)


def _solar_score_from_kp(kp_index: float) -> float:
    # Lower Kp means quieter conditions and cleaner focus.
    return max(0.0, min(100.0, 100.0 - (kp_index * 10.0)))


def _lunar_score(state: CosmicState) -> float:
    illum = max(0.0, min(100.0, state.lunar_illumination))
    phase = state.moon_phase.lower()

    if "waxing" in phase:
        phase_bias = 12
    elif "full" in phase:
        phase_bias = 18
    elif "new" in phase:
        phase_bias = 6
    elif "waning" in phase:
        phase_bias = -8
    else:
        phase_bias = 0

    return max(0.0, min(100.0, illum + phase_bias))


def _tidal_score(state: CosmicState) -> float:
    raw = 50.0 + (state.tide_range_m * 10.0) + (state.tide_slope * 40.0)
    return max(0.0, min(100.0, raw))


def compute_energy_score(
    *,
    kp_index: float,
    cosmic_state: CosmicState,
    market_compression_score: float,
) -> float:
    solar_score = _solar_score_from_kp(kp_index)
    lunar_score = _lunar_score(cosmic_state)
    tidal_score = _tidal_score(cosmic_state)

    energy = (
        0.35 * solar_score
        + 0.25 * lunar_score
        + 0.20 * tidal_score
        + 0.20 * max(0.0, min(100.0, market_compression_score))
    )
    return round(energy, 1)


def classify_regime(energy_score: float, cvi: float, data_quality_guard: bool = False) -> tuple[str, str]:
    if data_quality_guard:
        return "GUARD MODE", "NO_TRADE"

    if cvi >= 5:
        return "SOLAR STORM", "REDUCE_SIZE"

    if energy_score >= 80:
        return "BREAKOUT", "EXECUTE"
    if energy_score >= 65:
        return "MOMENTUM", "TREND_TRADE"
    if energy_score >= 50:
        return "ACCUMULATION", "WAIT"
    return "RANGE", "WAIT"


def build_forecast(
    start_price: float,
    start_date: date,
    weekly_return_pct: float,
    days: int = 7,
) -> List[ForecastPoint]:
    """Build a smooth forecast curve with real calendar dates."""
    if days < 1:
        raise ValueError("days must be >= 1")

    target = start_price * (1.0 + weekly_return_pct / 100.0)
    path: List[ForecastPoint] = []

    for i in range(days + 1):
        # Gentle convex curve: slower start, faster finish.
        progress = (i / days) ** 1.15
        price = start_price + (target - start_price) * progress
        path.append(ForecastPoint(date=start_date + timedelta(days=i), price=round(price, 2)))
    return path


def build_snapshot(
    *,
    market: MarketState,
    space: SpaceWeather,
    cosmic: CosmicState,
    start_date: date,
    breakout_long_above: float | None = None,
    momentum_short_below: float | None = None,
    prime_trade_days: Iterable[str] | None = None,
) -> Snapshot:
    cvi = compute_cvi(space.kp_index, space.solar_wind_kms, space.xray_flux)
    energy_score = compute_energy_score(
        kp_index=space.kp_index,
        cosmic_state=cosmic,
        market_compression_score=market.market_compression_score,
    )
    regime, trade_signal = classify_regime(
        energy_score=energy_score,
        cvi=cvi,
        data_quality_guard=market.data_quality_guard,
    )
    forecast = build_forecast(
        start_price=market.btc_price,
        start_date=start_date,
        weekly_return_pct=market.weekly_return_pct,
        days=7,
    )

    notes = []
    if space.kp_index >= 5:
        notes.append("Kp storm threshold breached: volatility hedge active.")
    if market.data_quality_guard:
        notes.append("Data quality guard active: execution disabled.")
    if "waning" in cosmic.moon_phase.lower():
        notes.append("Waning moon: liquidity contraction bias.")
    if cosmic.tide_slope > 0:
        notes.append("Rising tide: energy building.")
    elif cosmic.tide_slope < 0:
        notes.append("Falling tide: release phase.")

    return Snapshot(
        market=market,
        space=space,
        cosmic=cosmic,
        forecast=forecast,
        cvi=cvi,
        energy_score=energy_score,
        regime=regime,
        trade_signal=trade_signal,
        notes=notes,
        breakout_long_above=breakout_long_above,
        momentum_short_below=momentum_short_below,
        prime_trade_days=list(prime_trade_days or []),
    )
