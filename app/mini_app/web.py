"""
HABESHAGO Mini App Web Server

Serves the HABESHAGO Mini App locally using Flask.
"""

from flask import Flask, jsonify, render_template, request

from datetime import datetime, timezone

from app.mini_app.pages.home import get_home_page
from app.mini_app.pages.passenger_dashboard import (
    get_passenger_dashboard,
)

from app.mini_app.pages.driver_dashboard import (
    get_driver_dashboard,
)

from app.mini_app.pages.driver_assignment import (
    get_driver_assignment_page,
)

from app.mini_app.services.dispatch_service import (
    find_best_driver,
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

from app.mini_app.pages.booking_summary import (
    get_booking_summary_page,
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

@app.route("/booking-summary")
def booking_summary():
    """
    Render the HABESHAGO Booking Summary.
    """

    page = get_booking_summary_page()

    return render_template(
        "booking_summary.html",
        page=page,
        active_page="home",
    )

@app.route("/driver-assignment")
def driver_assignment():
    """
    Render the assigned-driver result.
    """

    page = get_driver_assignment_page()

    return render_template(
        "driver_assignment.html",
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
                "selected_route": trip.selected_route,
                "booking_status": trip.booking_status,
                "created_at": trip.created_at,
            },
        }
    )

@app.route("/api/trip/service", methods=["POST"])
def update_trip_service():
    """
    Store the passenger's selected mobility service
    and its current planner estimates.
    """

    payload = request.get_json(silent=True) or {}

    service = str(
        payload.get("service", "")
    ).strip()

    estimated_eta = str(
        payload.get("estimated_eta", "")
    ).strip()

    recommendation = str(
        payload.get("recommendation", "")
    ).strip()

    try:
        estimated_fare = float(
            payload.get("estimated_fare")
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "message": "A valid estimated fare is required.",
            }
        ), 400

    allowed_services = {
        "ride",
        "transit",
        "walk_transit",
    }

    if service not in allowed_services:
        return jsonify(
            {
                "success": False,
                "message": "Invalid mobility service.",
            }
        ), 400

    trip = get_trip()

    if not trip.is_ready_for_planning():
        return jsonify(
            {
                "success": False,
                "message": (
                    "Complete the destination and pickup "
                    "before selecting a service."
                ),
            }
        ), 409

    trip.service = service
    trip.estimated_fare = estimated_fare
    trip.estimated_eta = estimated_eta
    trip.recommendation = recommendation
    trip.category = None
    trip.set_booking_status("service_selected")

    return jsonify(
        {
            "success": True,
            "message": "Mobility service selected.",
            "trip": {
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "estimated_eta": trip.estimated_eta,
                "recommendation": trip.recommendation,
                "selected_route": trip.selected_route,
                "booking_status": trip.booking_status,
                "created_at": trip.created_at,
            },
        }
    )

@app.route("/api/trip/category", methods=["POST"])
def update_trip_category():
    """
    Store the passenger's selected ride category.
    """

    payload = request.get_json(silent=True) or {}

    category = str(
        payload.get("category", "")
    ).strip()

    allowed_categories = {
        "economy",
        "standard",
        "premium",
        "ev",
    }

    if category not in allowed_categories:
        return jsonify(
            {
                "success": False,
                "message": "Invalid ride category.",
            }
        ), 400

    trip = get_trip()

    if trip.service != "ride":
        return jsonify(
            {
                "success": False,
                "message": (
                    "Ride categories are available only "
                    "when Ride is selected."
                ),
            }
        ), 409

    if trip.booking_status != "service_selected":
        return jsonify(
            {
                "success": False,
                "message": (
                    "Select Ride before choosing "
                    "a ride category."
                ),
            }
        ), 409

    trip.category = category
    trip.set_booking_status("category_selected")

    return jsonify(
        {
            "success": True,
            "message": "Ride category selected.",
            "trip": {
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "estimated_eta": trip.estimated_eta,
                "booking_status": trip.booking_status,
            },
        }
    )

@app.route("/api/trip/confirm", methods=["POST"])
def confirm_trip_booking():
    """
    Validate and confirm the active passenger booking.

    The confirmed booking is then marked as ready
    for the future Dispatch Engine.
    """

    trip = get_trip()

    if not trip.is_ready_for_booking():
        return jsonify(
            {
                "success": False,
                "message": (
                    "The trip is incomplete and cannot "
                    "be confirmed."
                ),
            }
        ), 409

    if trip.service == "ride" and not trip.category:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Choose a ride category before "
                    "confirming the booking."
                ),
            }
        ), 409

    allowed_confirmation_states = {
        "service_selected",
        "category_selected",
        "summary_ready",
    }

    if trip.booking_status not in allowed_confirmation_states:
        return jsonify(
            {
                "success": False,
                "message": (
                    "This booking cannot be confirmed "
                    "from its current state."
                ),
            }
        ), 409

    trip.set_booking_status("summary_ready")

    trip.created_at = datetime.now(
        timezone.utc
    ).isoformat()

    trip.set_booking_status("booking_confirmed")

    # Commit #67 will begin processing bookings
    # that have reached this state.
    trip.set_booking_status("dispatch_pending")

    return jsonify(
        {
            "success": True,
            "message": (
                "Booking confirmed and prepared "
                "for driver dispatch."
            ),
            "trip": {
                "destination": trip.destination,
                "pickup_name": trip.pickup_name,
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "estimated_eta": trip.estimated_eta,
                "booking_status": trip.booking_status,
                "created_at": trip.created_at,
            },
        }
    )

@app.route("/api/trip/dispatch", methods=["POST"])
def dispatch_trip():
    """
    Find and assign the best available driver
    to the active passenger booking.
    """

    trip = get_trip()

    if trip.booking_status != "dispatch_pending":
        return jsonify(
            {
                "success": False,
                "message": (
                    "The booking must be dispatch pending "
                    "before driver search can begin."
                ),
            }
        ), 409

    trip.set_booking_status("driver_searching")

    driver = find_best_driver(trip)

    if driver is None:
        trip.set_booking_status("dispatch_failed")

        return jsonify(
            {
                "success": False,
                "message": "No available driver was found.",
                "trip": {
                    "booking_status": trip.booking_status,
                },
            }
        ), 404

    trip.assigned_driver_id = driver.driver_id
    trip.assigned_driver_name = driver.name
    trip.assigned_driver_rating = driver.rating
    trip.assigned_vehicle = driver.vehicle
    trip.assigned_vehicle_color = driver.vehicle_color
    trip.assigned_plate_number = driver.plate_number
    trip.driver_eta_minutes = driver.eta_minutes

    trip.set_booking_status("driver_assigned")

    return jsonify(
        {
            "success": True,
            "message": "Driver assigned successfully.",
            "trip": {
                "booking_status": trip.booking_status,
                "assigned_driver_id": trip.assigned_driver_id,
                "assigned_driver_name": trip.assigned_driver_name,
                "assigned_driver_rating": (
                    trip.assigned_driver_rating
                ),
                "assigned_vehicle": trip.assigned_vehicle,
                "assigned_vehicle_color": (
                    trip.assigned_vehicle_color
                ),
                "assigned_plate_number": (
                    trip.assigned_plate_number
                ),
                "driver_eta_minutes": (
                    trip.driver_eta_minutes
                ),
            },
        }
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )  