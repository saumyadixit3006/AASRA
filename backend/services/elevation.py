import requests


def get_elevation(latitude: float, longitude: float):
    """
    Fetch elevation for a location using the Open-Meteo
    elevation API.
    """

    url = "https://api.open-meteo.com/v1/elevation"

    params = {
        "latitude": latitude,
        "longitude": longitude
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    elevations = data.get("elevation", [])

    if not elevations:
        return None

    return elevations[0]
