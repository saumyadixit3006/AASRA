import requests

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

params = {
    "format": "geojson",
    "limit": 100,
    "orderby": "time",
    "minmagnitude": 4.0
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

events = response.json()["features"]

print("EARTHQUAKE DETECTION TEST")
print("Events found:", len(events))

for event in events:
    p = event["properties"]
    coordinates = event["geometry"]["coordinates"]

    print("-" * 40)
    print("Place:", p.get("place"))
    print("Magnitude:", p.get("mag"))
    print("Latitude:", coordinates[1])
    print("Longitude:", coordinates[0])
    print("Details:", p.get("url"))