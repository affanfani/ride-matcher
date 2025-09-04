from pydantic import BaseModel, Field, PositiveFloat, field_validator
from typing import Optional, Literal
from datetime import datetime

class RideCreate(BaseModel):
    """Schema for creating a new ride request"""
    pickup_lat: float = Field(..., description="Pickup latitude")
    pickup_lon: float = Field(..., description="Pickup longitude")
    dropoff_lat: float = Field(..., description="Dropoff latitude")
    dropoff_lon: float = Field(..., description="Dropoff longitude")
    price: PositiveFloat = Field(..., description="Price for the ride")

    @field_validator("pickup_lat", "dropoff_lat")
    @classmethod
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("pickup_lon", "dropoff_lon")
    @classmethod
    def validate_lon(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

class RideAccept(BaseModel):
    """Schema for accepting a ride - driver_id comes from authentication"""
    pass

class RideOut(BaseModel):
    """Schema for ride output/response"""
    id: int
    rider_id: str
    driver_id: Optional[str] = None
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    price: float
    status: Literal["pending", "accepted", "completed"]
    created_at: datetime

    class Config:
        from_attributes = True