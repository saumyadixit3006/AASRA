import requests
from datetime import datetime, timedelta, timezone

url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

# Try a recent date; imagery availability varies by layer.
day = datetime.now(timezone.utc).date() - timedelta(days=3)

params = {
    "SERVICE": "WMS",
    "REQUEST": "GetMap",
    "VERSION": "1.1.1",
    "LAYERS": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "SRS": "EPSG:4326",
    "BBOX": "-180,-90,180,90",
    "WIDTH": "1200",
    "HEIGHT": "600",
    "FORMAT": "image/png",
    "TIME": day.isoformat()
}

try:
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    if "image/" not in response.headers.get("Content-Type", ""):
        print("The server returned something other than an image.")
        print(response.text[:500])
    else:
        with open("satellite_test.png", "wb") as file:
            file.write(response.content)

        print("Success! Satellite image saved as satellite_test.png")
        print("Image date requested:", day)

except requests.RequestException as error:
    print("API request failed:", error)