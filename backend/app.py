
import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.weather import get_weather
from services.earthquake import get_earthquakes
from services.satellite import get_satellite_layer
from services.satellite_connection import search_asf_sentinel1
from risk.flood import calculate_flood_risk
from risk.cyclone import calculate_cyclone_risk
from risk.earthquake import calculate_earthquake_risk

from schemas import (
    FloodRiskInput,
    CycloneRiskInput,
    EarthquakeRiskInput,
)

# The API can start even if the trained-model service
# has not been added to the repository yet.
try:
    from services.flood_model import predict_flood
except ImportError:
    predict_flood = None


app = FastAPI(
    title="AASRA API",
    description=(
        "Disaster monitoring and risk assessment API "
        "for floods, cyclones, and earthquakes."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# HOME AND HEALTH
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "AASRA",
        "full_name": "All-Hazard AI for Safety, Risk and Alerts",
        "status": "running",
        "version": "1.0.0",
        "supported_hazards": [
            "Floods",
            "Cyclones",
            "Earthquakes",
        ],
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AASRA Backend",
    }


# ---------------------------------------------------------
# LIVE WEATHER
# ---------------------------------------------------------

@app.get("/api/weather")
def weather(
    latitude: float = 23.2599,
    longitude: float = 77.4126,
):
    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90.",
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )

    try:
        return get_weather(latitude, longitude)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Weather service failed: {str(exc)}",
        )


# ---------------------------------------------------------
# RECENT EARTHQUAKE DATA
# ---------------------------------------------------------

@app.get("/api/earthquakes")
def earthquakes(
    latitude: float = 23.2599,
    longitude: float = 77.4126,
    radius_km: float = 500,
):
    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90.",
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )

    if not 0 < radius_km <= 20000:
        raise HTTPException(
            status_code=400,
            detail="Radius must be greater than 0 and at most 20000 km.",
        )

    try:
        return get_earthquakes(
            latitude,
            longitude,
            radius_km,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Earthquake service failed: {str(exc)}",
        )


# ---------------------------------------------------------
# SATELLITE MAP LAYER
# ---------------------------------------------------------

@app.get("/api/satellite")
def satellite():
    try:
        return get_satellite_layer()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Satellite layer service failed: {str(exc)}",
        )


# ---------------------------------------------------------
# FLOOD RISK — RULE-BASED ASSESSMENT
# ---------------------------------------------------------

@app.post("/api/risk/flood")
def flood_risk(request: FloodRiskInput):
    try:
        return calculate_flood_risk(
            rainfall=request.rainfall,
            humidity=request.humidity,
            precipitation=request.precipitation,
            elevation=request.elevation,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Flood risk calculation failed: {str(exc)}",
        )


# ---------------------------------------------------------
# CYCLONE RISK — RULE-BASED ASSESSMENT
# ---------------------------------------------------------

@app.post("/api/risk/cyclone")
def cyclone_risk(request: CycloneRiskInput):
    try:
        return calculate_cyclone_risk(
            wind_speed=request.wind_speed,
            pressure=request.pressure,
            rainfall=request.rainfall,
            humidity=request.humidity,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Cyclone risk calculation failed: {str(exc)}",
        )


# ---------------------------------------------------------
# EARTHQUAKE RISK — EVENT IMPACT ASSESSMENT
# ---------------------------------------------------------

@app.post("/api/risk/earthquake")
def earthquake_risk(request: EarthquakeRiskInput):
    try:
        return calculate_earthquake_risk(
            magnitude=request.magnitude,
            depth_km=request.depth_km,
            distance_km=request.distance_km,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Earthquake risk calculation failed: {str(exc)}",
        )


# ---------------------------------------------------------
# TRAINED FLOOD MODEL — SENTINEL-1 GEOTIFF
# ---------------------------------------------------------

@app.post("/api/flood/predict")
async def flood_prediction(file: UploadFile = File(...)):
    if predict_flood is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Flood-model service is not installed. "
                "Add backend/services/flood_model.py and "
                "the trained model file before using this endpoint."
            ),
        )

    if not file.filename or not file.filename.lower().endswith(
        (".tif", ".tiff")
    ):
        raise HTTPException(
            status_code=400,
            detail="Upload a Sentinel-1 GeoTIFF (.tif or .tiff).",
        )

    temp_path = None

    try:
        suffix = os.path.splitext(file.filename)[1].lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        result = predict_flood(temp_path)

        return {
            "success": True,
            "hazard": "flood",
            "prediction_type": "satellite_water_segmentation",
            "message": (
                "Water segmentation completed. "
                "This identifies water in the uploaded image; "
                "it is not a future flood forecast."
            ),
            "prediction": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=(
                "Trained flood model not found. Check that "
                "backend/models/aasra_flood_unet_improved.pth "
                "exists."
            ),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Flood prediction failed: {str(exc)}",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


# Run with:
# uvicorn app:app --reload
