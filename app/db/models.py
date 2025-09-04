from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Float, Enum, DateTime, Boolean
from datetime import datetime
import enum
from typing import Optional

class Base(DeclarativeBase):
    pass

class RideStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"

class UserType(str, enum.Enum):
    RIDER = "rider"
    DRIVER = "driver"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rider_id: Mapped[str] = mapped_column(String(64), nullable=False)
    driver_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Pickup coordinates (lat, lon)
    pickup_lat: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_lon: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Dropoff coordinates (lat, lon)
    dropoff_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dropoff_lon: Mapped[float] = mapped_column(Float, nullable=False)

    # Price (float)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Status (pending/accepted/completed)
    status: Mapped[RideStatus] = mapped_column(Enum(RideStatus), default=RideStatus.PENDING, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
