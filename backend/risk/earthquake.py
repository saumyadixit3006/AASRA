def calculate_earthquake_risk(
    magnitude: float,
    depth_km: float,
    distance_km: float
):
    """
    Calculate a basic earthquake impact-risk score.

    This does NOT predict earthquakes.
    It estimates potential local impact based on
    magnitude, depth and distance from the event.
    """

    score = 0
    factors = []

    # Magnitude
    if magnitude >= 7:
        score += 50
        factors.append("Very strong earthquake")
    elif magnitude >= 6:
        score += 40
        factors.append("Strong earthquake")
    elif magnitude >= 5:
        score += 30
        factors.append("Moderate earthquake")
    elif magnitude >= 4:
        score += 15
        factors.append("Light earthquake")
    else:
        score += 5
        factors.append("Low-magnitude earthquake")

    # Depth
    if depth_km <= 10:
        score += 25
        factors.append("Shallow earthquake")
    elif depth_km <= 30:
        score += 15
        factors.append("Relatively shallow earthquake")
    elif depth_km <= 70:
        score += 8
        factors.append("Intermediate-depth earthquake")

    # Distance
    if distance_km <= 25:
        score += 25
        factors.append("Very close to selected location")
    elif distance_km <= 100:
        score += 15
        factors.append("Relatively close to selected location")
    elif distance_km <= 250:
        score += 8
        factors.append("Within regional distance")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "disaster": "Earthquake",
        "risk_score": score,
        "risk_level": level,
        "factors": factors,
        "assessment_type": "Event impact-risk assessment"
    }
