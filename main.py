from __future__ import annotations

from datetime import date

from reporting.terminal import render_terminal
from solar_sentinel.engine import build_snapshot
from solar_sentinel.models import CosmicState, MarketState, SpaceWeather


def main() -> None:
    market = MarketState(
        btc_price=71417,
        weekly_return_pct=7.24,
        ml_confidence_pct=99,
        breakout_probability_pct=35,
        vol_risk_pct=35,
        market_compression_score=91.5,
        posture="NO_TRADE",
        data_quality_guard=False,
    )

    space = SpaceWeather(
        kp_index=2.0,
        solar_wind_kms=410,
        xray_flux="B1.0",
        proton_flux="quiet",
    )

    cosmic = CosmicState(
        moon_phase="Waning Crescent",
        lunar_illumination=12,
        tide_range_m=1.00,
        tide_slope=0.00,
        solar_rotation_phase="20.0/27",
    )

    snapshot = build_snapshot(
        market=market,
        space=space,
        cosmic=cosmic,
        start_date=date(2026, 3, 15),
        breakout_long_above=71290,
        momentum_short_below=70744,
        prime_trade_days=["2026-03-26", "2026-03-27", "2026-04-10"],
    )

    render_terminal(snapshot)


if __name__ == "__main__":
    main()
