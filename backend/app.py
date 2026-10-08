from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.weather import get_weather
from services.earthquake import get_earthquakes
from services.satellite import get_satellite_layer

from risk.flood import calculate_flood_risk
from risk.cyclone import calculate_cyclone_risk
from risk.earthquake import calculate_earthquake_risk


app = FastAPI(
    title="AASRA API",
    description="AI-powered multi-disaster risk assessment system",
    version="1.0.0"
)


# Allow our frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------------------------------------
# BASIC ROUTES
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "AASRA",
        "message": "AASRA backend is running",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# LIVE WEATHER
# ---------------------------------------------------------

@app.get("/api/weather")
def weather(latitude: float, longitude: float):

    try:
        return get_weather(latitude, longitude)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch weather data: {str(error)}"
        )


# ---------------------------------------------------------
# LIVE EARTHQUAKE DATA
# ---------------------------------------------------------

@app.get("/api/earthquakes")
def earthquakes(
    latitude: float,
    longitude: float,
    radius_km: int = 500
):

    try:
        data = get_earthquakes(
            latitude,
            longitude,
            radius_km
        )

        return {
            "count": len(data),
            "earthquakes": data
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch earthquake data: {str(error)}"
        )


# ---------------------------------------------------------
# SATELLITE
# ---------------------------------------------------------

@app.get("/api/satellite")
def satellite():

    return get_satellite_layer()


# ---------------------------------------------------------
# FLOOD RISK
# ---------------------------------------------------------

@app.get("/api/risk/flood")
def flood_risk(
    rainfall: float,
    humidity: float,
    precipitation: float = 0,
    elevation: float = 100
):

    try:
        result = calculate_flood_risk(
            rainfall=rainfall,
            humidity=humidity,
            precipitation=precipitation,
            elevation=elevation
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to calculate flood risk: {str(error)}"
        )


# ---------------------------------------------------------
# CYCLONE RISK
# ---------------------------------------------------------

@app.get("/api/risk/cyclone")
def cyclone_risk(
    wind_speed: float,
    pressure: float,
    rainfall: float = 0,
    humidity: float = 0
):

    try:
        result = calculate_cyclone_risk(
            wind_speed=wind_speed,
            pressure=pressure,
            rainfall=rainfall,
            humidity=humidity
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to calculate cyclone risk: {str(error)}"
        )


# ---------------------------------------------------------
# EARTHQUAKE RISK
# ---------------------------------------------------------

@app.get("/api/risk/earthquake")
def earthquake_risk(
    magnitude: float,
    depth_km: float,
    distance_km: float
):

    try:
        result = calculate_earthquake_risk(
            magnitude=magnitude,
            depth_km=depth_km,
            distance_km=distance_km
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to calculate earthquake risk: {str(error)}"
        )
