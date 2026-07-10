"""
Stores the currently active ride for each driver.

Key:
    driver_id (Telegram ID)

Value:
    {
        "passenger_id": ...,
    }
"""

active_rides = {}