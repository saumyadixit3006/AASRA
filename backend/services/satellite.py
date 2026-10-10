import os
import requests
from requests.auth import HTTPBasicAuth


ASF_SEARCH_URL = "https://api.daac.asf.alaska.edu/services/search/param"


def get_satellite_layer():
    """
    Returns NASA GIBS imagery configuration
    for display on the AASRA map.
    """
    return {
        "name": "NASA GIBS Satellite",
        "type": "wms",
        "url": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",
        "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "format": "image/png",
        "transparent": True,
    }


def search_sentinel1(latitude, longitude, radius_km=25):
    """
    Search ASF for Sentinel-1 GRD scenes near a location.
    Returns scene metadata; it does not download the imagery.
    """
    params = {
        "platform": "Sentinel-1",
        "processingLevel": "GRD_HD",
        "intersectsWith": (
            f"POINT({longitude} {latitude})"
        ),
        "output": "json",
    }

    response = requests.get(
        ASF_SEARCH_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    scenes = response.json()

    return {
        "source": "ASF DAAC",
        "latitude": latitude,
        "longitude": longitude,
        "radius_km": radius_km,
        "count": len(scenes),
        "scenes": scenes,
    }
