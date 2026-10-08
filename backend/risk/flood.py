def calculate_flood_risk(
    rainfall: float,
    humidity: float,
    precipitation: float = 0,
    elevation: float = 100
):
    """
    Calculate a baseline flood risk score.

    This is a transparent rule-based assessment.
    It is not a trained machine-learning prediction model.
    """

    score = 0
    factors = []

    # Rainfall contribution
    if rainfall >= 100:
        score += 40
        factors.append("Very high rainfall")
    elif rainfall >= 50:
        score += 25
        factors.append("High rainfall")
    elif rainfall >= 20:
        score += 15
        factors.append("Moderate rainfall")

    # Current precipitation
    if precipitation >= 20:
        score += 20
        factors.append("Heavy current precipitation")
    elif precipitation >= 5:
        score += 10
        factors.append("Current precipitation detected")

    # Humidity
    if humidity >= 85:
        score += 15
        factors.append("Very high humidity")
    elif humidity >= 70:
        score += 8
        factors.append("High humidity")

    # Lower elevation generally increases flood vulnerability
    if elevation < 50:
        score += 20
        factors.append("Low elevation")
    elif elevation < 100:
        score += 10
        factors.append("Relatively low elevation")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MODERATE"
    else:
        level = "LOW"

    if not factors:
        factors.append("No major flood-risk factors detected")

    return {
        "disaster": "Flood",
        "risk_score": score,
        "risk_level": level,
        "factors": factors,
        "assessment_type": "Baseline rule-based assessment"
    }
