from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from solar_sentinel.engine import build_snapshot
from solar_sentinel.models import CosmicState, MarketState, Snapshot, SpaceWeather


def _parse_prime_trade_days(raw: str) -> List[str]:
    tokens: List[str] = []
    for chunk in raw.replace("\n", ",").split(","):
        value = chunk.strip()
        if value:
            tokens.append(value)
    return tokens


def _snapshot_to_json(snapshot: Snapshot) -> Dict[str, Any]:
    payload = asdict(snapshot)
    payload["forecast"] = [
        {"date": point.date.isoformat(), "price": point.price}
        for point in snapshot.forecast
    ]
    return payload


def _regime_banner(regime: str, signal: str) -> None:
    text = f"Regime: {regime} | Trade Signal: {signal}"
    if regime in {"GUARD MODE", "SOLAR STORM"}:
        st.error(text)
        return
    if regime in {"BREAKOUT", "MOMENTUM"}:
        st.success(text)
        return
    st.info(text)


def main() -> None:
    st.set_page_config(page_title="Solar Sentinel Webapp", layout="wide")
    st.title("Solar Sentinel Webapp")
    st.caption("Interactive dashboard version of your Solar Sentinel terminal model.")

    if "snapshot" not in st.session_state:
        st.session_state.snapshot = None

    with st.sidebar:
        st.header("Market Inputs")
        btc_price = st.number_input("BTC Price", min_value=0.0, value=71417.0, step=10.0)
        weekly_return_pct = st.number_input("Weekly Return (%)", value=7.24, step=0.1)
        ml_confidence_pct = st.slider("ML Confidence (%)", min_value=0.0, max_value=100.0, value=99.0, step=1.0)
        breakout_probability_pct = st.slider(
            "Breakout Probability (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0
        )
        vol_risk_pct = st.slider("Volatility Risk (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0)
        market_compression_score = st.slider(
            "Market Compression Score", min_value=0.0, max_value=100.0, value=91.5, step=0.5
        )
        posture = st.selectbox("Posture", options=["WAIT", "NO_TRADE", "EXECUTE", "REDUCE_SIZE"], index=1)
        data_quality_guard = st.checkbox("Data Quality Guard", value=False)

        st.header("Space Weather")
        kp_index = st.number_input("Kp Index", min_value=0.0, max_value=9.0, value=2.0, step=0.1)
        solar_wind_kms = st.number_input("Solar Wind (km/s)", min_value=0.0, value=410.0, step=10.0)
        xray_flux = st.text_input("X-ray Flux", value="B1.0")
        proton_flux = st.text_input("Proton Flux", value="quiet")

        st.header("Cosmic Inputs")
        moon_phase = st.selectbox(
            "Moon Phase",
            options=[
                "New Moon",
                "Waxing Crescent",
                "First Quarter",
                "Waxing Gibbous",
                "Full Moon",
                "Waning Gibbous",
                "Last Quarter",
                "Waning Crescent",
            ],
            index=7,
        )
        lunar_illumination = st.slider("Lunar Illumination (%)", min_value=0.0, max_value=100.0, value=12.0, step=1.0)
        tide_range_m = st.number_input("Tide Range (m)", min_value=0.0, value=1.0, step=0.05)
        tide_slope = st.number_input("Tide Slope", value=0.0, step=0.05)
        solar_rotation_phase = st.text_input("Solar Rotation Phase", value="20.0/27")

        st.header("Execution Levels")
        start_date = st.date_input("Start Date", value=date.today())
        breakout_long_above = st.number_input("Breakout Long Above", min_value=0.0, value=71290.0, step=10.0)
        momentum_short_below = st.number_input("Momentum Short Below", min_value=0.0, value=70744.0, step=10.0)
        prime_trade_days_raw = st.text_area(
            "Prime Trade Days (comma or new line)",
            value="2026-03-26, 2026-03-27, 2026-04-10",
            height=80,
        )

        run_model = st.button("Generate Snapshot", type="primary", use_container_width=True)

    if run_model or st.session_state.snapshot is None:
        market = MarketState(
            btc_price=float(btc_price),
            weekly_return_pct=float(weekly_return_pct),
            ml_confidence_pct=float(ml_confidence_pct),
            breakout_probability_pct=float(breakout_probability_pct),
            vol_risk_pct=float(vol_risk_pct),
            market_compression_score=float(market_compression_score),
            posture=posture,
            data_quality_guard=bool(data_quality_guard),
        )

        space = SpaceWeather(
            kp_index=float(kp_index),
            solar_wind_kms=float(solar_wind_kms),
            xray_flux=xray_flux.strip(),
            proton_flux=proton_flux.strip(),
        )

        cosmic = CosmicState(
            moon_phase=moon_phase,
            lunar_illumination=float(lunar_illumination),
            tide_range_m=float(tide_range_m),
            tide_slope=float(tide_slope),
            solar_rotation_phase=solar_rotation_phase.strip(),
        )

        snapshot = build_snapshot(
            market=market,
            space=space,
            cosmic=cosmic,
            start_date=start_date,
            breakout_long_above=float(breakout_long_above),
            momentum_short_below=float(momentum_short_below),
            prime_trade_days=_parse_prime_trade_days(prime_trade_days_raw),
        )
        st.session_state.snapshot = snapshot

    snapshot: Snapshot = st.session_state.snapshot
    _regime_banner(snapshot.regime, snapshot.trade_signal)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BTC", f"${snapshot.market.btc_price:,.0f}")
    c2.metric("CVI", f"{snapshot.cvi:.2f}")
    c3.metric("Energy Score", f"{snapshot.energy_score:.1f}")
    c4.metric("Kp", f"{snapshot.space.kp_index:.1f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Weekly Return", f"{snapshot.market.weekly_return_pct:+.2f}%")
    c6.metric("ML Confidence", f"{snapshot.market.ml_confidence_pct:.0f}%")
    c7.metric("Breakout Probability", f"{snapshot.market.breakout_probability_pct:.0f}%")
    c8.metric("Volatility Risk", f"{snapshot.market.vol_risk_pct:.0f}%")

    forecast_df = pd.DataFrame(
        [{"date": point.date, "price": point.price} for point in snapshot.forecast]
    )
    st.subheader("Forecast Path")
    st.line_chart(forecast_df.set_index("date")["price"], height=300)
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    st.subheader("Tactical Levels")
    t1, t2 = st.columns(2)
    t1.metric("Breakout Long Above", f"${snapshot.breakout_long_above:,.0f}" if snapshot.breakout_long_above else "N/A")
    t2.metric("Momentum Short Below", f"${snapshot.momentum_short_below:,.0f}" if snapshot.momentum_short_below else "N/A")

    st.write("Prime Trade Days:", ", ".join(snapshot.prime_trade_days) if snapshot.prime_trade_days else "None")

    if snapshot.notes:
        st.subheader("Desk Notes")
        for note in snapshot.notes:
            st.write(f"- {note}")

    with st.expander("Snapshot JSON"):
        st.json(_snapshot_to_json(snapshot))


if __name__ == "__main__":
    main()
