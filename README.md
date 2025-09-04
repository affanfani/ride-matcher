# 🚗 Ride Matcher API - FastAPI Assignment

A simplified ride-matching API built with FastAPI for the technical assignment. This system allows riders to request rides and drivers to accept them, with proper concurrency control and background notifications.

## 📋 Assignment Requirements Met

✅ **Async FastAPI Endpoints**
- `POST /api/v1/rides/` → Rider creates a ride request
- `GET /api/v1/rides/available/` → Driver fetches available rides  
- `POST /api/v1/rides/{ride_id}/accept/` → Driver accepts a ride

✅ **Data Model**
- Rider ID, Driver ID, Pickup (lat, lon), Dropoff (lat, lon), Price (float), Status (pending/accepted/completed)

✅ **Input Validation**
- Coordinates validation (lat: -90 to 90, lon: -180 to 180)
- Positive price validation
- Proper Pydantic models

✅ **Concurrency Control**
- Atomic database updates prevent race conditions
- Only one driver can accept a ride

✅ **Background Tasks**
- Rider notification via background task (simulated with print/log)

✅ **Deployment Ready**
- Auto-generated Swagger UI at `/docs`

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## 📚 API Endpoints

### Authentication Endpoints (JWT)

#### 1. Register User
```bash
POST /api/v1/auth/register
```
**Request Body:**
```json
{
  "email": "rider@example.com",
  "password": "securepass123",
  "full_name": "John Rider",
  "user_type": "rider"
}
```

#### 2. Login User
```bash
POST /api/v1/auth/login
```
**Request Body:**
```json
{
  "email": "rider@example.com",
  "password": "securepass123"
}
```

#### 3. Get Current User
```bash
GET /api/v1/auth/me
```
**Headers:** `Authorization: Bearer <token>`

### Core Endpoints (Assignment Requirements) - JWT Protected

#### 1. Create Ride Request (Rider Only)
```bash
POST /api/v1/rides/
```
**Headers:** `Authorization: Bearer <rider_token>`
**Request Body:**
```json
{
  "pickup_lat": 40.7128,
  "pickup_lon": -74.0060,
  "dropoff_lat": 40.7589,
  "dropoff_lon": -73.9851,
  "price": 25.50
}
```

#### 2. Get Available Rides (Driver Only)
```bash
GET /api/v1/rides/available/
```
**Headers:** `Authorization: Bearer <driver_token>`

#### 3. Accept Ride (Driver Only)
```bash
POST /api/v1/rides/{ride_id}/accept/
```
**Headers:** `Authorization: Bearer <driver_token>`

## 🏗️ Project Structure

```
ride-assignment/
├── app/
│   ├── main.py              # FastAPI application
│   ├── env_config.py        # Environment configuration
│   ├── core/
│   │   ├── config.py        # Settings management
│   │   └── middleware.py    # Validation middleware
│   ├── api/
│   │   ├── api.py           # API router with prefix
│   │   └── routes/
│   │       └── rides.py     # Ride endpoints
│   ├── db/
│   │   ├── models.py        # Database models
│   │   └── session.py       # Database session
│   ├── schemas/
│   │   └── rides.py         # Pydantic models
│   └── utils/
│       └── notifications.py # Background notifications
├── requirements.txt         # Dependencies
├── README.md               # This file
├── Procfile                # Heroku deployment
└── render.yaml             # Render deployment
```

## 📊 Example Usage

### 1. Register a Rider
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rider@example.com",
    "password": "securepass123",
    "full_name": "John Rider",
    "user_type": "rider"
  }'
```

### 2. Register a Driver
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver@example.com",
    "password": "securepass123",
    "full_name": "Jane Driver",
    "user_type": "driver"
  }'
```

### 3. Login as Rider
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rider@example.com",
    "password": "securepass123"
  }'
# Save the access_token from response
```

### 4. Create a Ride Request (as authenticated rider)
```bash
curl -X POST "http://localhost:8000/api/v1/rides/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <rider_access_token>" \
  -d '{
    "pickup_lat": 40.7128,
    "pickup_lon": -74.0060,
    "dropoff_lat": 40.7589,
    "dropoff_lon": -73.9851,
    "price": 25.50
  }'
```

### 5. Login as Driver and Get Available Rides
```bash
# First login as driver to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver@example.com",
    "password": "securepass123"
  }'

# Then get available rides
curl -X GET "http://localhost:8000/api/v1/rides/available/" \
  -H "Authorization: Bearer <driver_access_token>"
```

### 6. Accept a Ride (as authenticated driver)
```bash
curl -X POST "http://localhost:8000/api/v1/rides/1/accept/" \
  -H "Authorization: Bearer <driver_access_token>"
```

## 🔧 Configuration

Database and application settings are in `app/env_config.py`:
- SQLite database (default)
- Development environment
- JWT settings (for optional challenge)

## 🚀 Deployment

### Deploy to Heroku
```bash
# Create Procfile (already included)
# Push to Heroku
heroku create your-app-name
git push heroku main
```

### Deploy to Render
```bash
# Connect GitHub repository to Render
# render.yaml configuration is included
```

## 🔄 Concurrency Control

The API ensures race-condition-safe ride acceptance using:
- **Atomic Updates**: Database-level atomic operations
- **Status Checking**: Only pending rides can be accepted
- **Single Transaction**: Prevents multiple drivers accepting the same ride

Example of the concurrency control mechanism:
```python
stmt = (
    update(Ride)
    .where(and_(Ride.id == ride_id, Ride.status == RideStatus.PENDING))
    .values(status=RideStatus.ACCEPTED, driver_id=driver_id)
)
result = await session.execute(stmt)
if result.rowcount == 0:
    raise HTTPException(409, "Ride already accepted")
```

## 📱 Background Notifications

When a driver accepts a ride, the rider is notified via a background task:
```python
background_tasks.add_task(notify_rider, ride.rider_id, ride.id, ride.driver_id)
```

The notification is simulated with print/log output as required by the assignment.

## 🧪 Testing

Test the API using the interactive Swagger UI at `/docs` or with curl commands as shown above.

## ⚡ Assignment Completion Time

This implementation focuses on the core requirements and can be completed within the 60-90 minute timeframe specified in the assignment.

---

**Built with FastAPI following clean, maintainable, and idiomatic Python practices.**