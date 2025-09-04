from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from fastapi import HTTPException, status, Depends
from typing import List
from datetime import datetime
import logging

from app.db.models import Ride, RideStatus
from app.schemas.rides import RideCreate, RideOut, RideAccept
from app.db.session import get_session

logger = logging.getLogger(__name__)

class RideService:
    """Service class for ride operations with dependency injection"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ride(self, payload: RideCreate, rider_id: str) -> RideOut:
        """Create a new ride request"""
        try:
            ride = Ride(
                rider_id=rider_id,
                pickup_lat=payload.pickup_lat,
                pickup_lon=payload.pickup_lon,
                dropoff_lat=payload.dropoff_lat,
                dropoff_lon=payload.dropoff_lon,
                price=payload.price,
                status=RideStatus.PENDING,
            )
            
            self.session.add(ride)
            await self.session.commit()
            await self.session.refresh(ride)
            
            logger.info(f"Created ride {ride.id} for rider {rider_id}")
            return ride
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create ride: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create ride"
            )

    async def get_available_rides(self) -> List[RideOut]:
        """Get available rides"""
        try:
            stmt = select(Ride).where(Ride.status == RideStatus.PENDING).order_by(Ride.created_at.desc())
            result = await self.session.execute(stmt)
            rides = result.scalars().all()
            
            return rides
            
        except Exception as e:
            logger.error(f"Failed to get available rides: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve rides"
            )

    async def accept_ride(self, ride_id: int, driver_id: str) -> RideOut:
        """Accept a ride with proper concurrency control"""
        try:
            # Use atomic UPDATE with WHERE conditions for concurrency safety
            stmt = (
                update(Ride)
                .where(
                    and_(
                        Ride.id == ride_id,
                        Ride.status == RideStatus.PENDING  # Only pending rides can be accepted
                    )
                )
                .values(
                    status=RideStatus.ACCEPTED,
                    driver_id=driver_id
                )
                .execution_options(synchronize_session=False)
            )
            
            result = await self.session.execute(stmt)
            
            # Check if exactly one row was affected (ride exists and was pending)
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ride not found, already accepted, or not available"
                )
            
            await self.session.commit()
            
            # Fetch the updated ride
            ride = await self.session.get(Ride, ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found after acceptance"
                )
            
            logger.info(f"Driver {driver_id} accepted ride {ride_id}")
            return ride
            
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to accept ride {ride_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to accept ride"
            )

# Dependency injection function
def get_ride_service(session: AsyncSession = Depends(get_session)) -> RideService:
    """Dependency injection for RideService"""
    return RideService(session)