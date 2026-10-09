import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.weather import get_weather
from services.earthquake import get_earthquakes
from services.satellite import get_satellite_layer

from risk.flood import calculate_flood_risk
from risk.cyclone import calculate_cyclone_risk
from risk.earthquake import calculate_earthquake_risk

from schemas import (
    FloodRiskRequest,
    CycloneRiskRequest,
    EarthquakeRiskRequest,
)

from services.flood_model import predict_flood


# ============================================================
# AASRA — All-Hazard AI for Safety, Risk and Alerts
# FastAPI Backend
# ============================================================

app = FastAPI(
    title="AASRA API",
    description=(
        "Disaster monitoring and risk assessment API "
        "for floods, cyclones, and earthquakes."
    ),
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# BASIC ENDPOINTS
# ============================================================

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


# ============================================================
# WEATHER DATA
# ============================================================

@app.get("/api/weather")
def weather(
    latitude: float = 23.2599,
    longitude: float = 77.4126,
):
    try:
        return get_weather(latitude, longitude)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Weather service failed: {str(exc)}",
        )


# ============================================================
# EARTHQUAKE DATA
# ============================================================

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


# ============================================================
# SATELLITE MAP LAYER
# ============================================================

@app.get("/api/satellite")
def satellite():
    try:
        return get_satellite_layer()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Satellite layer service failed: {str(exc)}",
        )


# ============================================================
# FLOOD RISK ASSESSMENT — EXISTING RULE-BASED MODEL
# ============================================================

@app.post("/api/risk/flood")
def flood_risk(request: FloodRiskRequest):
    try:
        return calculate_flood_risk(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Flood risk calculation failed: {str(exc)}",
        )


# ============================================================
# CYCLONE RISK ASSESSMENT — EXISTING RULE-BASED MODEL
# ============================================================

@app.post("/api/risk/cyclone")
def cyclone_risk(request: CycloneRiskRequest):
    try:
        return calculate_cyclone_risk(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Cyclone risk calculation failed: {str(exc)}",
        )


# ============================================================
# EARTHQUAKE RISK ASSESSMENT — EXISTING RULE-BASED MODEL
# ============================================================

@app.post("/api/risk/earthquake")
def earthquake_risk(request: EarthquakeRiskRequest):
    try:
        return calculate_earthquake_risk(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Earthquake risk calculation failed: {str(exc)}",
        )


# ============================================================
# TRAINED FLOOD SEGMENTATION MODEL
# Accepts a two-band Sentinel-1 GeoTIFF.
# ============================================================

@app.post("/api/flood/predict")
async def flood_prediction(file: UploadFile = File(...)):
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
                "This output is not a future flood forecast."
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
                "Trained flood model not found. "
                "Check backend/models/aasra_flood_unet_improved.pth."
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


# ============================================================
# RUN LOCALLY:
# uvicorn app:app --reload
# ============================================================
