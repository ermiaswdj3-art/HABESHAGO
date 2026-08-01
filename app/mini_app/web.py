"""
HABESHAGO Mini App Web Server

Serves the HABESHAGO Mini App locally using Flask.
"""

from flask import Flask, jsonify, render_template, request

from app.mini_app.pages.home import get_home_page
from app.mini_app.pages.passenger_dashboard import (
    get_passenger_dashboard,
)

from app.mini_app.pages.driver_dashboard import (
    get_driver_dashboard,
)

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.mini_app.context import (
    get_trip,
    reset_trip,
    set_destination,
    set_pickup,
)

from app.mini_app.pages.trip_planner import (
    get_trip_planner_page,
)

from app.mini_app.pages.map import get_map_page

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

def reverse_geocode_pickup(
    latitude: float,
    longitude: float,
) -> str:
    """
    Convert pickup coordinates into a readable place name.

    Returns a safe fallback when the external geocoding
    service is unavailable or has no suitable result.
    """

    fallback_name = "Selected on Map"

    query = urlencode(
        {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
            "zoom": 18,
        }
    )

    url = (
        "https://nominatim.openstreetmap.org/reverse?"
        f"{query}"
    )

    request_headers = {
        "User-Agent": (
            "HABESHAGO-Mini-App/0.1 "
            "(development contact: project owner)"
        ),
        "Accept-Language": "en",
    }

    request_object = Request(
        url,
        headers=request_headers,
    )

    try:
        with urlopen(
            request_object,
            timeout=5,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )
    except (
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return fallback_name

    address = payload.get("address", {})

    place_name = (
        payload.get("name")
        or address.get("amenity")
        or address.get("building")
        or address.get("road")
        or address.get("neighbourhood")
        or address.get("suburb")
        or address.get("city_district")
        or address.get("city")
        or address.get("town")
        or address.get("village")
    )

    if not place_name:
        return fallback_name

    area_name = (
        address.get("suburb")
        or address.get("city_district")
        or address.get("city")
    )

    if area_name and area_name != place_name:
        return f"{place_name}, {area_name}"

    return str(place_name)

@app.route("/")
def home():
    """
    Render the HABESHAGO ecosystem home page.
    """

    page = get_home_page()

    return render_template(
        "home.html",
        page=page,
        active_page="home",
    )


@app.route("/passenger")
def passenger_dashboard():
    """
    Render the HABESHAGO passenger dashboard.
    """

    page = get_passenger_dashboard()

    return render_template(
        "passenger_dashboard.html",
        page=page,
        active_page="passenger",
    )

@app.route("/driver")
def driver_dashboard():
    """
    Render the HABESHAGO driver dashboard.
    """

    page = get_driver_dashboard()

    return render_template(
        "driver_dashboard.html",
        page=page,
        active_page="driver",
    )

@app.route("/map")
def map_page():
    """
    Render the HABESHAGO interactive pickup map.
    """

    page = get_map_page()

    return render_template(
        "map.html",
        page=page,
        active_page="home",
    )

@app.route("/trip-planner")
def trip_planner():
    """
    Render the HABESHAGO Trip Planner.
    """

    page = get_trip_planner_page()

    return render_template(
        "trip_planner.html",
        page=page,
        active_page="home",
    )

@app.route("/api/trip/destination", methods=["POST"])
def update_trip_destination():
    """
    Store the passenger's selected destination
    in the active Trip Context.
    """

    payload = request.get_json(silent=True) or {}

    destination = str(
        payload.get("destination", "")
    ).strip()

    if not destination:
        return jsonify(
            {
                "success": False,
                "message": "Destination is required.",
            }
        ), 400

    # A new destination begins a new journey and clears
    # any pickup information left from an earlier trip.
    reset_trip()
    set_destination(destination)

    trip = get_trip()

    return jsonify(
        {
            "success": True,
            "message": "Destination saved successfully.",
            "trip": {
                "destination": trip.destination,
                "pickup_name": trip.pickup_name,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
            },
        }
    )

@app.route("/api/trip/pickup", methods=["POST"])
def update_trip_pickup():
    """
    Store the passenger's selected pickup location
    in the active Trip Context.
    """

    payload = request.get_json(silent=True) or {}

    try:
        latitude = float(payload.get("latitude"))
        longitude = float(payload.get("longitude"))
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "message": "Valid pickup coordinates are required.",
            }
        ), 400

    pickup_name = reverse_geocode_pickup(
        latitude=latitude,
        longitude=longitude,
    )
    trip = get_trip()

    if not trip.destination:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Please choose a destination before "
                    "confirming pickup."
                ),
            }
        ), 409

    set_pickup(
        latitude=latitude,
        longitude=longitude,
        name=pickup_name,
    )

    trip = get_trip()

    return jsonify(
        {
            "success": True,
            "message": "Pickup saved successfully.",
            "trip": {
                "destination": trip.destination,
                "pickup_name": trip.pickup_name,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
            },
        }
    )

@app.route("/api/trip", methods=["GET"])
def read_active_trip():
    """
    Return the active trip stored in the running Flask process.
    """

    trip = get_trip()

    return jsonify(
        {
            "success": True,
            "trip": {
                "destination": trip.destination,
                "pickup_name": trip.pickup_name,
                "pickup_latitude": trip.pickup_latitude,
                "pickup_longitude": trip.pickup_longitude,
                "passengers": trip.passengers,
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "estimated_eta": trip.estimated_eta,
                "recommendation": trip.recommendation,
            },
        }
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )  