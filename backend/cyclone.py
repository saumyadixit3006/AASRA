def calculate_cyclone_risk(
    wind_speed: float,
    pressure: float,
    rainfall: float = 0,
    humidity: float = 0
):
    """
    Calculate a baseline cyclone-related risk score.

    This assessment uses environmental indicators.
    It does not predict cyclone formation or track.
    """

    score = 0
    factors = []

    # Wind speed
    if wind_speed >= 100:
        score += 45
        factors.append("Extremely strong winds")
    elif wind_speed >= 60:
        score += 30
        factors.append("Strong winds")
    elif wind_speed >= 40:
        score += 20
        factors.append("Elevated wind speed")
    elif wind_speed >= 25:
        score += 10
        factors.append("Moderate wind speed")

    # Atmospheric pressure
    if pressure < 990:
        score += 30
        factors.append("Very low atmospheric pressure")
    elif pressure < 1000:
        score += 20
        factors.append("Low atmospheric pressure")
    elif pressure < 1010:
        score += 10
        factors.append("Slightly reduced atmospheric pressure")

    # Rainfall
    if rainfall >= 50:
        score += 15
        factors.append("Heavy rainfall")
    elif rainfall >= 20:
        score += 8
        factors.append("Moderate rainfall")

    # Humidity
    if humidity >= 85:
        score += 10
        factors.append("Very high humidity")
    elif humidity >= 70:
        score += 5
        factors.append("High humidity")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MODERATE"
    else:
        level = "LOW"

    if not factors:
        factors.append("No major cyclone-related risk factors detected")

    return {
        "disaster": "Cyclone",
        "risk_score": score,
        "risk_level": level,
        "factors": factors,
        "assessment_type": "Baseline environmental assessment"
    }
