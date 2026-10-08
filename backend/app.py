from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.weather import get_weather
from services.earthquake import get_earthquakes
from services.satellite import get_satellite_layer


app = FastAPI(
    title="AASRA API",
    description="AI-powered multi-disaster risk assessment system",
    version="1.0.0"
)


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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


@app.get("/api/weather")
def weather(latitude: float, longitude: float):

    try:
        return get_weather(latitude, longitude)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch weather data: {str(error)}"
        )


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


@app.get("/api/satellite")
def satellite():

    return get_satellite_layer()
