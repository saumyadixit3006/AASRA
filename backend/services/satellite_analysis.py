def analyze_satellite_data(
    water_detected: bool = False,
    water_change_percent: float = 0
):
    """
    Convert satellite-derived water observations into
    a flood evidence score.

    This function is designed to accept actual satellite
    observations once the Sentinel-1 / OPERA pipeline
    is connected.
    """

    score = 0
    factors = []

    if water_detected:
        score += 60
        factors.append(
            "Water detected in satellite observation"
        )

    if water_change_percent >= 50:
        score += 40
        factors.append(
            "Significant increase in surface water"
        )

    elif water_change_percent >= 20:
        score += 25
        factors.append(
            "Increase in surface water"
        )

    score = min(
        score,
        100
    )

    if not factors:
        factors.append(
            "No significant satellite water evidence"
        )

    return {
        "satellite_score": score,
        "factors": factors
    }
