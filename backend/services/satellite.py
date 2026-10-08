def get_satellite_layer():
    """
    Returns the NASA GIBS satellite imagery layer
    that can be displayed on the AASRA map.
    """

    return {
        "name": "NASA GIBS Satellite",
        "type": "wms",
        "url": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",
        "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "format": "image/png",
        "transparent": True
    }
