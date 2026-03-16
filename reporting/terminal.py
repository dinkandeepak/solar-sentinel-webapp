from __future__ import annotations

from datetime import datetime

from solar_sentinel.models import Snapshot


def _color(text: str, fg: str) -> str:
    palette = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    return f"{palette.get(fg, '')}{text}{palette['reset']}"


def _regime_color(regime: str) -> str:
    mapping = {
        "GUARD MODE": "red",
        "SOLAR STORM": "red",
        "BREAKOUT": "green",
        "MOMENTUM": "green",
        "ACCUMULATION": "yellow",
        "RANGE": "blue",
    }
    return mapping.get(regime, "cyan")


def render_terminal(snapshot: Snapshot) -> None:
    regime_color = _regime_color(snapshot.regime)

    print()
    print(_color("=" * 78, "bold"))
    print(_color("SOLAR SENTINEL MASTER TERMINAL", "bold"))
    print(_color("=" * 78, "bold"))

    print(
        f"BTC ${snapshot.market.btc_price:,.0f}  |  "
        f"CVI {snapshot.cvi:.2f}  |  "
        f"Energy {snapshot.energy_score:.1f}  |  "
        f"Kp {snapshot.space.kp_index:.1f}  |  "
        f"Posture {snapshot.trade_signal}"
    )

    print(
        f"Moon {snapshot.cosmic.moon_phase} ({snapshot.cosmic.lunar_illumination:.0f}%)"
        f"  |  Tide range {snapshot.cosmic.tide_range_m:.2f} m"
        f"  |  Tide slope {snapshot.cosmic.tide_slope:+.2f}"
    )

    print(_color(f"Regime: {snapshot.regime}", regime_color))
    print("-" * 78)

    print("WEEKLY ML PATH")
    print(
        f"Return {snapshot.market.weekly_return_pct:+.2f}%  |  "
        f"Confidence {snapshot.market.ml_confidence_pct:.0f}%  |  "
        f"Breakout {snapshot.market.breakout_probability_pct:.0f}%  |  "
        f"Vol Risk {snapshot.market.vol_risk_pct:.0f}%"
    )

    for point in snapshot.forecast:
        print(f"  {point.date.isoformat()}  ->  ${point.price:,.2f}")

    print("-" * 78)
    print("TACTICAL LEVELS")
    if snapshot.breakout_long_above is not None:
        print(f"  Breakout long above : ${snapshot.breakout_long_above:,.0f}")
    if snapshot.momentum_short_below is not None:
        print(f"  Momentum short below: ${snapshot.momentum_short_below:,.0f}")

    if snapshot.prime_trade_days:
        print("  Prime trade days    : " + ", ".join(snapshot.prime_trade_days))

    if snapshot.notes:
        print("-" * 78)
        print("DESK NOTES")
        for note in snapshot.notes:
            print(f"  - {note}")

    print("-" * 78)
    print("Updated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
    print(_color("=" * 78, "bold"))


