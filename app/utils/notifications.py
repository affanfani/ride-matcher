import logging

logger = logging.getLogger(__name__)

def notify_rider(rider_id: str, ride_id: int, driver_id: str):
    """Notify rider via background task when ride is accepted (simulated with print/log)"""
    notification_message = f"🚗 NOTIFICATION: Rider {rider_id}, your ride {ride_id} was accepted by driver {driver_id}"
    
    # Print to console (as per assignment requirement)
    print(notification_message)
    
    # Also log it
    logger.info(notification_message)