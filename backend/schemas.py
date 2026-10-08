from pydantic import BaseModel, Field


# ---------------------------------------------------------
# FLOOD RISK INPUT
# ---------------------------------------------------------

class FloodRiskInput(BaseModel):
    rainfall: float = Field(
        ...,
        ge=0,
        description="Rainfall in millimeters"
    )

    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage"
    )

    precipitation: float = Field(
        0,
        ge=0,
        description="Current precipitation in millimeters"
    )

    elevation: float = Field(
        100,
        ge=0,
        description="Elevation above sea level in meters"
    )


# ---------------------------------------------------------
# CYCLONE RISK INPUT
# ---------------------------------------------------------

class CycloneRiskInput(BaseModel):
    wind_speed: float = Field(
        ...,
        ge=0,
        description="Wind speed in km/h"
    )

    pressure: float = Field(
        ...,
        gt=0,
        description="Atmospheric pressure in hPa"
    )

    rainfall: float = Field(
        0,
        ge=0,
        description="Rainfall in millimeters"
    )

    humidity: float = Field(
        0,
        ge=0,
        le=100,
        description="Relative humidity percentage"
    )


# ---------------------------------------------------------
# EARTHQUAKE RISK INPUT
# ---------------------------------------------------------

class EarthquakeRiskInput(BaseModel):
    magnitude: float = Field(
        ...,
        ge=0,
        le=10,
        description="Earthquake magnitude"
    )

    depth_km: float = Field(
        ...,
        ge=0,
        description="Earthquake depth in kilometers"
    )

    distance_km: float = Field(
        ...,
        ge=0,
        description="Distance from selected location in kilometers"
    )
