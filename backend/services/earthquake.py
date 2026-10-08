import requests


def get_earthquakes(latitude: float, longitude: float, radius_km: int = 500):
    """
    Fetch recent earthquakes around the selected location
    using the USGS Earthquake API.
    """

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    params = {
        "format": "geojson",
        "latitude": latitude,
        "longitude": longitude,
        "maxradiuskm": radius_km,
        "limit": 20,
        "orderby": "time"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    earthquakes = []

    for feature in data.get("features", []):
        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get("coordinates", [])

        if len(coordinates) < 3:
            continue

        earthquakes.append({
            "place": properties.get("place"),
            "magnitude": properties.get("mag"),
            "time": properties.get("time"),
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "depth": coordinates[2],
            "url": properties.get("url")
        })

    return earthquakes
