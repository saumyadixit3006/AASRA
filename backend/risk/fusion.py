def calculate_final_risk(
    ml_score: float,
    live_score: float,
    satellite_score: float = 0
):
    """
    Combine ML prediction, live environmental conditions
    and satellite evidence into a final AASRA risk score.

    The weights are intentionally transparent and can be
    calibrated after validation with real data.
    """

    final_score = (
        (ml_score * 0.50) +
        (live_score * 0.30) +
        (satellite_score * 0.20)
    )

    final_score = max(
        0,
        min(100, final_score)
    )

    if final_score >= 70:
        risk_level = "HIGH"

    elif final_score >= 40:
        risk_level = "MODERATE"

    else:
        risk_level = "LOW"

    return {
        "risk_score": round(
            final_score,
            2
        ),
        "risk_level": risk_level,
        "components": {
            "ml_score": ml_score,
            "live_score": live_score,
            "satellite_score": satellite_score
        }
    }
