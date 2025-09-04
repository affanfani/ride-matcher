from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.session import get_session
from app.db.models import User
from app.schemas.rides import RideCreate, RideOut, RideAccept
from app.services.rides import RideService, get_ride_service
from app.utils.notifications import notify_rider
from app.utils.auth import get_current_rider, get_current_driver

router = APIRouter(tags=["rides"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=RideOut, status_code=status.HTTP_201_CREATED)
async def create_ride(
    payload: RideCreate,
    current_user: User = Depends(get_current_rider),
    ride_service: RideService = Depends(get_ride_service),
):
    """Rider creates a ride request (requires authentication)"""
    return await ride_service.create_ride(payload, current_user.id)

@router.get("/available/", response_model=List[RideOut])
async def get_available_rides(
    current_user: User = Depends(get_current_driver),
    ride_service: RideService = Depends(get_ride_service),
):
    """Driver fetches available rides (requires authentication)"""
    return await ride_service.get_available_rides()

@router.post("/{ride_id}/accept/", response_model=RideOut)
async def accept_ride(
    ride_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_driver),
    ride_service: RideService = Depends(get_ride_service),
):
    """Driver accepts a ride (requires authentication)"""
    ride = await ride_service.accept_ride(ride_id, current_user.id)
    
    # Add background notification task
    background_tasks.add_task(notify_rider, ride.rider_id, ride.id, ride.driver_id)
    
    return ride