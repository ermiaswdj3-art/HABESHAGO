"""
Stores each driver's currently active ride.

Key:
    driver_id — Telegram ID of the driver

Value:
    {
        "ride_id": int,
        "passenger_id": int,
        "pickup": (latitude, longitude),
        "destination": (latitude, longitude),
        "distance": float,
        "fare": float,
        "service_type": str,
        "status": str,          # Present after recovery
        "recovered": bool,      # Present after recovery
    }

The dictionary normally lives in memory.

During HABESHAGO startup, unfinished rides are
restored from SQLite by recovery_service.py.
"""

active_rides = {}