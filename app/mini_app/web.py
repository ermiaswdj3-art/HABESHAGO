"""
HABESHAGO Mini App Web Server

Serves the HABESHAGO Mini App locally using Flask.
"""

from flask import Flask, jsonify, render_template, request

from datetime import datetime, timezone

from app.mini_app.repositories import get_driver_by_id

from app.mini_app.pages.home import get_home_page
from app.mini_app.pages.passenger_dashboard import (
    get_passenger_dashboard,
)

from app.mini_app.pages.driver_dashboard import (
    get_driver_dashboard,
)

from app.mini_app.pages.payment import (
    get_payment_page,
)

from app.mini_app.services.fare_breakdown_service import (
    calculate_fare_breakdown,
)

from app.mini_app.services.payment_service import (
    process_payment,
    select_payment_method,
)

from app.mini_app.services.payment_service import (
    SUPPORTED_PAYMENT_METHODS,
    process_payment,
    select_payment_method,
)

from app.mini_app.pages.active_trip import (
    get_active_trip_page,
)

from app.mini_app.pages.driver_assignment import (
    get_driver_assignment_page,
)

from app.mini_app.services.tracking_service import (
    calculate_distance_km as calculate_tracking_distance_km,
    move_driver_toward_pickup,
)

from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4

from app.config.settings import (
    BOT_TOKEN,
)

from app.mini_app.auth import (
    authenticate_mini_app_driver,
    authenticate_mini_app_passenger,
)

from app.mini_app.ride_integration import (
    MiniAppPricingAdapterError,
    MiniAppRideLifecycleBridgeError,
    MiniAppRouteMeasurementAdapterError,
    accept_offer_and_bind_trip,
    measure_mini_app_route,
    orchestrate_mini_app_ride_offer,
    price_mini_app_ride_estimate,
)

from app.mini_app.services.payment_service import (
    SUPPORTED_PAYMENT_METHODS,
    process_payment,
    select_payment_method,
)

from app.mini_app.services.pickup_verification_service import (
    generate_pickup_pin,
    verify_pickup_pin,
)

from app.mini_app.services.trip_lifecycle_service import (
    advance_trip_progress,
    complete_trip,
    start_trip,
)

from app.mini_app.services.ride_lifecycle_integration_service import (
    MiniAppCanonicalRideLifecycleError,
    mark_driver_en_route,
    mark_driver_arrived,
    mark_passenger_on_board,
    mark_trip_started,
    mark_trip_completed,
)

from app.mini_app.services.ride_state_synchronization_service import (
    MiniAppRideStateSynchronizationError,
    synchronize_trip_with_canonical_ride,
)

from app.mini_app.services.passenger_synchronization_recovery_service import (
    MiniAppPassengerSynchronizationRecoveryError,
    recover_passenger_synchronization,
)

from app.mini_app.services.passenger_synchronization_resume_service import (
    MiniAppPassengerSynchronizationResumeError,
    resume_passenger_synchronization,
)

from app.mini_app.services.dispatch_service import (
    find_best_driver,
)

from app.services.ride_offer_service import (
    get_driver_pending_offer,
    reject_driver_ride_offer,
)

from app.services.geocoding_service import (
    get_location_details,
)

from app.services.destination_search_service import (
    search_destinations,
)

from app.services.synchronization_service import (
    acknowledge_pending_passenger_update_in_order,
    get_pending_passenger_updates,
    get_pending_passenger_updates_after_sequence,
)

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
    Resolve pickup coordinates through the shared
    HABESHAGO geocoding platform.

    The Mini App intentionally delegates location
    understanding to the same canonical service used
    by the Telegram ride experience.
    """

    location = get_location_details(
        latitude=latitude,
        longitude=longitude,
        language="en",
    )

    return location["short_name"]


@app.route(
    "/api/location/reverse",
    methods=["GET"],
)
def reverse_geocode_location():
    """
    Resolve coordinates into structured HABESHAGO
    passenger-facing location context.
    """

    try:
        latitude = float(
            request.args.get("latitude")
        )
        longitude = float(
            request.args.get("longitude")
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Valid latitude and longitude "
                    "are required."
                ),
            }
        ), 400

    location = get_location_details(
        latitude=latitude,
        longitude=longitude,
        language="en",
    )

    return jsonify(
        {
            "success": True,
            "location": {
                "short_name": (
                    location["short_name"]
                ),
                "city": location["city"],
                "full_name": (
                    location["full_name"]
                ),
                "latitude": (
                    location["latitude"]
                ),
                "longitude": (
                    location["longitude"]
                ),
            },
        }
    )


@app.route(
    "/api/destinations/search",
    methods=["GET"],
)
def search_mini_app_destinations():
    """
    Search canonical HABESHAGO destinations for the
    Mini App passenger experience.

    Results come from the shared destination search
    platform already used by the Telegram client.
    """

    query = str(
        request.args.get(
            "q",
            "",
        )
    ).strip()

    if len(query) < 2:
        return jsonify(
            {
                "success": True,
                "destinations": [],
            }
        )

    destinations = search_destinations(
        query=query,
        language="en",
    )

    return jsonify(
        {
            "success": True,
            "destinations": destinations,
        }
    )


@app.route(
    "/health",
    methods=["GET"],
)
def mini_app_health():
    """
    Return the public HABESHAGO Mini App liveness status.

    This endpoint intentionally avoids database mutation
    and external provider calls so deployment platforms
    can determine whether the web process is alive.
    """

    return jsonify(
        {
            "status": "ok",
            "service": "habeshago-mini-app",
        }
    )

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

@app.route("/active-trip")
def active_trip():
    """
    Render the active passenger trip.
    """

    page = get_active_trip_page()

    return render_template(
        "active_trip.html",
        page=page,
        active_page="home",
    )

@app.route("/api/trip/destination", methods=["POST"])
def update_trip_destination():
    """
    Store the passenger's selected destination
    in the active Trip Context.

    Destination coordinates are accepted when available.

    They remain optional temporarily so the existing
    demonstration destination flow continues to work
    while HABESHAGO transitions to canonical location
    context.
    """

    payload = request.get_json(silent=True) or {}

    destination = str(
        payload.get(
            "destination",
            "",
        )
    ).strip()

    if not destination:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Destination is required."
                ),
            }
        ), 400

    latitude = payload.get(
        "latitude"
    )

    longitude = payload.get(
        "longitude"
    )

    # Either both destination coordinates must be
    # supplied or neither may be supplied.
    if (
        latitude is None
        and longitude is None
    ):
        destination_latitude = None
        destination_longitude = None

    elif (
        latitude is None
        or longitude is None
    ):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Destination latitude and longitude "
                    "must be provided together."
                ),
            }
        ), 400

    else:
        try:
            destination_latitude = float(
                latitude
            )

            destination_longitude = float(
                longitude
            )

        except (
            TypeError,
            ValueError,
        ):
            return jsonify(
                {
                    "success": False,
                    "message": (
                        "Valid destination coordinates "
                        "are required."
                    ),
                }
            ), 400

        if not (
            -90.0
            <= destination_latitude
            <= 90.0
        ):
            return jsonify(
                {
                    "success": False,
                    "message": (
                        "Destination latitude is out "
                        "of range."
                    ),
                }
            ), 400

        if not (
            -180.0
            <= destination_longitude
            <= 180.0
        ):
            return jsonify(
                {
                    "success": False,
                    "message": (
                        "Destination longitude is out "
                        "of range."
                    ),
                }
            ), 400

    # A new destination begins a new journey and clears
    # any pickup information left from an earlier trip.
    reset_trip()

    set_destination(
        destination,
        latitude=destination_latitude,
        longitude=destination_longitude,
    )

    trip = get_trip()

    return jsonify(
        {
            "success": True,
            "message": (
                "Destination saved successfully."
            ),
            "trip": {
                "destination": (
                    trip.destination
                ),
                "destination_latitude": (
                    trip.destination_latitude
                ),
                "destination_longitude": (
                    trip.destination_longitude
                ),
                "pickup_name": (
                    trip.pickup_name
                ),
                "pickup_latitude": (
                    trip.pickup_latitude
                ),
                "pickup_longitude": (
                    trip.pickup_longitude
                ),
                "trip_started_at": (
                    trip.trip_started_at
                ),
                "trip_completed_at": (
                    trip.trip_completed_at
                ),
                "trip_progress_percent": (
                    trip.trip_progress_percent
                ),
                "destination_reached": (
                    trip.destination_reached
                ),
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

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 401

    try:
        measurement = measure_mini_app_route(
            trip=trip,
        )
    except (
        MiniAppRouteMeasurementAdapterError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 400

    calculated_at = datetime.now(
        timezone.utc
    )

    try:
        pricing = price_mini_app_ride_estimate(
            passenger_id=passenger.passenger_id,
            measurement=measurement,
            service_type="ride",
            ride_category=category,
            city="Addis Ababa",
            quote_id=(
                f"MINI-EST-{uuid4().hex}"
            ),
            calculated_at=calculated_at,
        )
    except (
        MiniAppPricingAdapterError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 400

    trip.category = category
    trip.estimated_fare = pricing.fare
    trip.fare_currency = pricing.currency
    trip.set_booking_status(
        "category_selected"
    )

    return jsonify(
        {
            "success": True,
            "message": "Ride category selected.",
            "trip": {
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "fare_currency": trip.fare_currency,
                "estimated_eta": trip.estimated_eta,
                "booking_status": trip.booking_status,
                "pricing_quote_id": pricing.quote_id,
                "pricing_configuration_version": (
                    pricing.configuration_version
                ),
            },
        }
    )

@app.route("/api/trip/confirm", methods=["POST"])
def confirm_trip_booking():
    """
    Authenticate and authoritatively confirm the active
    Mini App passenger Ride booking.

    Confirmation establishes trusted passenger identity,
    canonical route measurement and authoritative
    pre-dispatch pricing before the booking becomes
    eligible for driver dispatch.
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

    if trip.service != "ride":
        return jsonify(
            {
                "success": False,
                "message": (
                    "Authoritative Mini App confirmation "
                    "currently supports Ride bookings only."
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

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = authenticate_mini_app_passenger(
            init_data=init_data,
            bot_token=BOT_TOKEN,
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 401

    try:
        measurement = measure_mini_app_route(
            trip=trip,
        )
    except (
        MiniAppRouteMeasurementAdapterError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 400

    calculated_at = datetime.now(
        timezone.utc
    )

    try:
        pricing = price_mini_app_ride_estimate(
            passenger_id=passenger.passenger_id,
            measurement=measurement,
            service_type="ride",
            ride_category=trip.category,
            city="Addis Ababa",
            quote_id=(
                f"MINI-CONF-{uuid4().hex}"
            ),
            calculated_at=calculated_at,
        )
    except (
        MiniAppPricingAdapterError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
            }
        ), 400

    trip.canonical_passenger_id = (
        passenger.passenger_id
    )
    trip.estimated_fare = pricing.fare
    trip.fare_currency = pricing.currency
    trip.pricing_quote_id = pricing.quote_id
    trip.pricing_configuration_version = (
        pricing.configuration_version
    )
    trip.route_measurement_reference = (
        measurement.measurement_reference
    )

    confirmed_at = calculated_at.isoformat()

    trip.created_at = confirmed_at
    trip.booking_confirmed_at = confirmed_at

    trip.set_booking_status(
        "summary_ready"
    )
    trip.set_booking_status(
        "booking_confirmed"
    )
    trip.set_booking_status(
        "dispatch_pending"
    )

    return jsonify(
        {
            "success": True,
            "message": (
                "Booking authoritatively confirmed and "
                "prepared for driver dispatch."
            ),
            "trip": {
                "destination": trip.destination,
                "pickup_name": trip.pickup_name,
                "service": trip.service,
                "category": trip.category,
                "estimated_fare": trip.estimated_fare,
                "fare_currency": trip.fare_currency,
                "estimated_eta": trip.estimated_eta,
                "booking_status": trip.booking_status,
                "created_at": trip.created_at,
                "booking_confirmed_at": (
                    trip.booking_confirmed_at
                ),
                "canonical_passenger_id": (
                    trip.canonical_passenger_id
                ),
                "pricing_quote_id": (
                    trip.pricing_quote_id
                ),
                "pricing_configuration_version": (
                    trip.pricing_configuration_version
                ),
                "route_measurement_reference": (
                    trip.route_measurement_reference
                ),
            },
        }
    )

@app.route("/api/trip/dispatch", methods=["POST"])
def dispatch_trip():
    """
    Authenticate the Telegram Mini App passenger and create
    one canonical pending HABESHAGO Ride Offer.

    This endpoint does not create a Ride directly.

    Canonical Ride creation occurs only after the selected
    driver accepts the pending Ride Offer.
    """

    trip = get_trip()

    if trip.booking_status != "dispatch_pending":
        return jsonify(
            {
                "success": False,
                "error": (
                    "Trip is not ready for dispatch."
                ),
            }
        ), 409

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        measurement = measure_mini_app_route(
            trip=trip,
        )
    except (
        MiniAppRouteMeasurementAdapterError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    driver = find_best_driver(
        trip
    )

    if driver is None:
        return jsonify(
            {
                "success": False,
                "error": (
                    "No eligible driver is currently "
                    "available."
                ),
            }
        ), 404

    if driver.pickup_distance_km is None:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Canonical driver pickup distance "
                    "is unavailable."
                ),
            }
        ), 409

    if driver.eta_minutes is None:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Canonical driver pickup ETA "
                    "is unavailable."
                ),
            }
        ), 409

    if not trip.payment_method:
        return jsonify(
            {
                "success": False,
                "error": (
                    "A payment method must be selected "
                    "before dispatch."
                ),
            }
        ), 409

    try:
        result = orchestrate_mini_app_ride_offer(
            trip=trip,
            passenger=passenger,
            driver=driver,
            measurement=measurement,
            pickup_distance_km=(
                driver.pickup_distance_km
            ),
            pickup_eta_minutes=(
                int(
                    driver.eta_minutes
                )
            ),
            payment_method=(
                trip.payment_method
            ),
            city="Addis Ababa",
            quote_id=(
                f"MINI-{uuid4().hex}"
            ),
            calculated_at=(
                datetime.now(
                    timezone.utc
                )
            ),
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    offer = result.offer

    trip.booking_status = "offer_pending"

    trip.assigned_driver_id = (
        driver.driver_id
    )
    trip.assigned_driver_name = (
        driver.name
    )
    trip.assigned_driver_rating = (
        driver.rating
    )
    trip.assigned_driver_vehicle = (
        driver.vehicle
    )
    trip.assigned_driver_plate = (
        driver.plate_number
    )
    trip.assigned_driver_color = (
        driver.vehicle_color
    )
    trip.driver_eta_minutes = (
        driver.eta_minutes
    )

    return jsonify(
        {
            "success": True,
            "status": "offer_pending",
            "offer_reference": (
                offer["offer_reference"]
            ),
            "driver": {
                "id": driver.driver_id,
                "name": driver.name,
                "rating": driver.rating,
                "vehicle": driver.vehicle,
                "plate_number": (
                    driver.plate_number
                ),
                "vehicle_color": (
                    driver.vehicle_color
                ),
                "eta_minutes": (
                    driver.eta_minutes
                ),
            },
            "pricing": {
                "quote_id": (
                    result.pricing.quote.quote_id
                ),
                "currency": (
                    result.pricing.quote.currency
                ),
                "fare": str(
                    result.pricing.fare
                ),
            },
        }
    )

@app.route(
    "/api/driver/offers/pending",
    methods=["GET"],
)
def get_authenticated_driver_pending_offer():
    """
    Return the authenticated Telegram Mini App driver's
    current canonical pending Ride Offer.

    The browser never supplies driver_id directly.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App driver "
                    "authentication data is required."
                ),
            }
        ), 401

    try:
        authenticated_driver = (
            authenticate_mini_app_driver(
                init_data=init_data,
                bot_token=BOT_TOKEN,
                require_operational=True,
            )
        )

    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    offer = get_driver_pending_offer(
        authenticated_driver.driver_id
    )

    if offer is None:
        return jsonify(
            {
                "success": True,
                "status": "no_pending_offer",
                "offer": None,
            }
        )

    return jsonify(
        {
            "success": True,
            "status": "offer_pending",
            "offer": offer,
        }
    )

@app.route(
    "/api/driver/offers/<int:offer_id>/reject",
    methods=["POST"],
)
def reject_authenticated_driver_offer(
    offer_id: int,
):
    """
    Authenticate the Telegram Mini App driver and reject
    that driver's current canonical pending Ride Offer.

    The browser never supplies driver_id directly.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App driver "
                    "authentication data is required."
                ),
            }
        ), 401

    try:
        authenticated_driver = (
            authenticate_mini_app_driver(
                init_data=init_data,
                bot_token=BOT_TOKEN,
                require_operational=True,
            )
        )

    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    pending_offer = get_driver_pending_offer(
        authenticated_driver.driver_id
    )

    if pending_offer is None:
        return jsonify(
            {
                "success": False,
                "error": (
                    "No pending Ride Offer exists "
                    "for this driver."
                ),
            }
        ), 404

    if (
        pending_offer.get("offer_id")
        != offer_id
    ):
        return jsonify(
            {
                "success": False,
                "error": (
                    "Ride Offer does not belong to "
                    "the authenticated driver."
                ),
            }
        ), 403

    try:
        rejected_offer = (
            reject_driver_ride_offer(
                offer_id
            )
        )

    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "status": "offer_rejected",
            "offer": rejected_offer,
        }
    )

@app.route(
    "/api/passenger/context",
    methods=["GET"],
)
def get_authenticated_passenger_context():
    """
    Return trusted passenger identity and Ethiopia-local greeting
    for the authenticated Telegram Mini App passenger.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    from datetime import datetime
    from zoneinfo import ZoneInfo

    local_now = datetime.now(
        ZoneInfo("Africa/Addis_Ababa")
    )

    hour = local_now.hour

    if 5 <= hour < 12:
        greeting_period = "Good Morning"
    elif 12 <= hour < 18:
        greeting_period = "Good Afternoon"
    else:
        greeting_period = "Good Evening"

    first_name = (
        passenger.telegram_identity.first_name
    )

    return jsonify(
        {
            "success": True,
            "first_name": first_name,
            "greeting": (
                f"{greeting_period}, "
                f"{first_name} 👋"
            ),
            "timezone": "Africa/Addis_Ababa",
        }
    )

@app.route(
    "/api/driver/offers/<int:offer_id>/accept",
    methods=["POST"],
)
def accept_driver_offer(
    offer_id: int,
):
    """
    Authenticate the Telegram Mini App driver, accept one
    canonical pending Ride Offer, create the authoritative
    HABESHAGO Ride, and bind that same Ride identity to the
    active Mini App Trip.

    The browser never supplies driver_id directly.
    """

    trip = get_trip()

    if trip.booking_status != "offer_pending":
        return jsonify(
            {
                "success": False,
                "error": (
                    "Trip is not waiting for driver "
                    "acceptance."
                ),
            }
        ), 409

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App driver "
                    "authentication data is required."
                ),
            }
        ), 401

    try:
        authenticated_driver = (
            authenticate_mini_app_driver(
                init_data=init_data,
                bot_token=BOT_TOKEN,
                require_operational=True,
            )
        )

    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        lifecycle_result = (
            accept_offer_and_bind_trip(
                trip=trip,
                offer_id=offer_id,
                driver_id=(
                    authenticated_driver.driver_id
                ),
            )
        )

    except (
        MiniAppRideLifecycleBridgeError,
        TypeError,
        ValueError,
    ) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    acceptance = (
        lifecycle_result.acceptance
    )

    integration = (
        lifecycle_result.integration
    )

    ride_id = acceptance.get(
        "ride_id"
    )

    if (
        ride_id is None
        or integration.reference.ride_id
        != ride_id
    ):
        return jsonify(
            {
                "success": False,
                "error": (
                    "Accepted Ride identity does not "
                    "match the Mini App Ride binding."
                ),
            }
        ), 409

    trip.set_booking_status(
        "driver_assigned"
    )

    return jsonify(
        {
            "success": True,
            "status": "driver_assigned",
            "ride_id": ride_id,
            "offer_id": acceptance.get(
                "offer_id"
            ),
            "offer_reference": acceptance.get(
                "offer_reference"
            ),
            "passenger_id": acceptance.get(
                "passenger_id"
            ),
            "driver_id": acceptance.get(
                "driver_id"
            ),
            "trip": {
                "booking_status": (
                    trip.booking_status
                ),
                "canonical_ride_id": (
                    trip.canonical_ride_id
                ),
                "canonical_passenger_id": (
                    trip.canonical_passenger_id
                ),
                "canonical_driver_id": (
                    trip.canonical_driver_id
                ),
                "assigned_driver_id": (
                    trip.assigned_driver_id
                ),
                "assigned_driver_name": (
                    trip.assigned_driver_name
                ),
            },
        }
    )

@app.route("/api/trip/tracking/update", methods=["POST"])
def update_driver_tracking():
    """
    Move the assigned driver toward the passenger pickup
    while routing Ride lifecycle changes through the
    authoritative HABESHAGO Ride Platform.

    Repeated tracking updates do not repeat an already
    applied canonical DRIVER_EN_ROUTE transition.
    """

    trip = get_trip()

    allowed_tracking_states = {
        "driver_assigned",
        "driver_arriving",
    }

    if trip.booking_status not in allowed_tracking_states:
        return jsonify(
            {
                "success": False,
                "message": (
                    "The trip must have an assigned driver "
                    "before tracking can begin."
                ),
            }
        ), 409

    if not trip.assigned_driver_id:
        return jsonify(
            {
                "success": False,
                "message": "No assigned driver was found.",
            }
        ), 409

    driver = get_driver_by_id(
        trip.assigned_driver_id
    )

    if driver is None:
        return jsonify(
            {
                "success": False,
                "message": (
                    "The assigned driver record was not found."
                ),
            }
        ), 404

    previous_booking_status = (
        trip.booking_status
    )

    move_driver_toward_pickup(
        driver=driver,
        trip=trip,
        progress_ratio=0.25,
    )

    remaining_distance_km = (
        calculate_tracking_distance_km(
            driver.latitude,
            driver.longitude,
            trip.pickup_latitude,
            trip.pickup_longitude,
        )
    )

    arrival_threshold_km = 0.02

    lifecycle_result = None

    if (
        remaining_distance_km
        <= arrival_threshold_km
    ):
        try:
            lifecycle_result = (
                mark_driver_arrived(
                    trip=trip,
                )
            )
        except (
            MiniAppCanonicalRideLifecycleError
        ) as error:
            return jsonify(
                {
                    "success": False,
                    "message": str(error),
                }
            ), 409

        driver.latitude = (
            trip.pickup_latitude
        )
        driver.longitude = (
            trip.pickup_longitude
        )
        driver.eta_minutes = 0

        driver.set_driver_status(
            "waiting"
        )

        trip.driver_eta_minutes = 0

    else:
        trip.driver_eta_minutes = (
            driver.eta_minutes
        )

        # Only the first movement after assignment
        # advances the authoritative Ride lifecycle.
        if (
            previous_booking_status
            == "driver_assigned"
        ):
            try:
                lifecycle_result = (
                    mark_driver_en_route(
                        trip=trip,
                    )
                )
            except (
                MiniAppCanonicalRideLifecycleError
            ) as error:
                return jsonify(
                    {
                        "success": False,
                        "message": str(error),
                    }
                ), 409

    return jsonify(
        {
            "success": True,
            "message": "Driver tracking updated.",
            "tracking": {
                "driver_id": driver.driver_id,
                "driver_name": driver.name,
                "latitude": driver.latitude,
                "longitude": driver.longitude,
                "remaining_distance_km": round(
                    remaining_distance_km,
                    3,
                ),
                "eta_minutes": (
                    driver.eta_minutes
                ),
                "driver_status": (
                    driver.driver_status
                ),
                "booking_status": (
                    trip.booking_status
                ),
                "has_arrived": (
                    trip.booking_status
                    == "driver_arrived"
                ),
                "canonical_transition_applied": (
                    lifecycle_result
                    is not None
                ),
                "canonical_state": (
                    lifecycle_result.canonical_state
                    if lifecycle_result
                    is not None
                    else None
                ),
            },
        }
    )

@app.route(
    "/api/trip/pickup-verification/start",
    methods=["POST"],
)
def start_pickup_verification():
    """
    Generate a pickup PIN after the assigned driver arrives.
    """

    trip = get_trip()

    if trip.booking_status == "pickup_verification_pending":
        return jsonify(
            {
                "success": True,
                "message": "Pickup verification is already active.",
                "verification": {
                    "pickup_pin": trip.pickup_pin,
                    "booking_status": trip.booking_status,
                    "pickup_pin_generated_at": (
                        trip.pickup_pin_generated_at
                    ),
                },
            }
        )

    try:
        pickup_pin = generate_pickup_pin(trip)
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Pickup PIN generated successfully.",
            "verification": {
                "pickup_pin": pickup_pin,
                "booking_status": trip.booking_status,
                "pickup_pin_generated_at": (
                    trip.pickup_pin_generated_at
                ),
            },
        }
    )

@app.route(
    "/api/trip/pickup-verification/verify",
    methods=["POST"],
)
def verify_trip_pickup():
    """
    Verify the pickup PIN and transition the
    authoritative Ride into passenger-on-board state.
    """

    payload = request.get_json(silent=True) or {}

    submitted_pin = str(
        payload.get("pickup_pin", "")
    ).strip()

    if not submitted_pin:
        return jsonify(
            {
                "success": False,
                "message": "Pickup PIN is required.",
            }
        ), 400

    trip = get_trip()

    try:
        is_verified = verify_pickup_pin(
            trip=trip,
            submitted_pin=submitted_pin,
            project_ready_state=False,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    if not is_verified:
        return jsonify(
            {
                "success": False,
                "message": "Incorrect pickup PIN.",
                "verification": {
                    "booking_status": (
                        trip.booking_status
                    ),
                    "pickup_verification_attempts": (
                        trip.pickup_verification_attempts
                    ),
                },
            }
        ), 401

    try:
        lifecycle_result = (
            mark_passenger_on_board(
                trip=trip,
            )
        )
    except MiniAppCanonicalRideLifecycleError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "verification": {
                    "booking_status": (
                        trip.booking_status
                    ),
                    "pickup_pin_verified": (
                        trip.pickup_pin_verified
                    ),
                    "canonical_transition": False,
                },
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": (
                "Passenger verified. "
                "The trip is ready to start."
            ),
            "verification": {
                "booking_status": (
                    trip.booking_status
                ),
                "pickup_pin_verified": (
                    trip.pickup_pin_verified
                ),
                "pickup_verified_at": (
                    trip.pickup_verified_at
                ),
                "pickup_verification_attempts": (
                    trip.pickup_verification_attempts
                ),
                "canonical_ride_id": (
                    lifecycle_result.ride_id
                ),
                "canonical_driver_id": (
                    lifecycle_result.driver_id
                ),
                "canonical_state": (
                    lifecycle_result.canonical_state
                ),
            },
        }
    )

@app.route("/api/trip/start", methods=["POST"])
def start_active_trip():
    """
    Start the active trip through the authoritative
    HABESHAGO Ride lifecycle.
    """

    trip = get_trip()

    try:
        start_trip(
            trip,
            project_lifecycle_state=False,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    try:
        lifecycle_result = mark_trip_started(
            trip=trip,
        )
    except MiniAppCanonicalRideLifecycleError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Trip started successfully.",
            "trip": {
                "booking_status": (
                    trip.booking_status
                ),
                "trip_started_at": (
                    trip.trip_started_at
                ),
                "trip_progress_percent": (
                    trip.trip_progress_percent
                ),
                "destination_reached": (
                    trip.destination_reached
                ),
                "canonical_ride_id": (
                    lifecycle_result.ride_id
                ),
                "canonical_driver_id": (
                    lifecycle_result.driver_id
                ),
                "canonical_state": (
                    lifecycle_result.canonical_state
                ),
            },
        }
    )

@app.route(
    "/api/trip/progress",
    methods=["POST"],
)
def update_trip_progress():
    """
    Advance the active trip toward its destination.
    """

    payload = request.get_json(silent=True) or {}

    try:
        progress_increment = int(
            payload.get("progress_increment", 20)
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "message": (
                    "A valid progress increment is required."
                ),
            }
        ), 400

    trip = get_trip()

    try:
        advance_trip_progress(
            trip=trip,
            progress_increment=progress_increment,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Trip progress updated.",
            "trip": {
                "booking_status": trip.booking_status,
                "trip_progress_percent": (
                    trip.trip_progress_percent
                ),
                "destination_reached": (
                    trip.destination_reached
                ),
            },
        }
    )

@app.route(
    "/api/trip/complete",
    methods=["POST"],
)
def complete_active_trip():
    """
    Complete the active trip through the authoritative
    HABESHAGO Ride lifecycle.

    The Mini App prepares completion metadata first, but
    it does not independently claim that the Ride has
    completed. The canonical Ride transition must succeed
    before the Mini App projects trip_completed.
    """

    trip = get_trip()

    try:
        complete_trip(
            trip,
            project_lifecycle_state=False,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    try:
        lifecycle_result = (
            mark_trip_completed(
                trip=trip,
            )
        )
    except MiniAppCanonicalRideLifecycleError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Trip completed successfully.",
            "trip": {
                "booking_status": (
                    trip.booking_status
                ),
                "trip_progress_percent": (
                    trip.trip_progress_percent
                ),
                "destination_reached": (
                    trip.destination_reached
                ),
                "trip_completed_at": (
                    trip.trip_completed_at
                ),
                "canonical_ride_id": (
                    lifecycle_result.ride_id
                ),
                "canonical_driver_id": (
                    lifecycle_result.driver_id
                ),
                "canonical_state": (
                    lifecycle_result.canonical_state
                ),
            },
        }
    )

@app.route(
    "/api/trip/payment/prepare",
    methods=["POST"],
)
def prepare_trip_payment():
    """
    Calculate the completed trip's final fare and
    prepare it for payment-method selection.

    Commit #71 currently uses controlled distance and
    duration values. Real route measurements will replace
    them in a later pricing integration.
    """

    trip = get_trip()

    if trip.booking_status != "trip_completed":
        return jsonify(
            {
                "success": False,
                "message": (
                    "Payment can be prepared only after "
                    "the trip is completed."
                ),
            }
        ), 409

    try:
        fare_result = calculate_fare_breakdown(
            trip=trip,
            distance_km=4.0,
            duration_minutes=12.0,
            waiting_minutes=0.0,
            airport_fee=0.0,
            toll_fee=0.0,
            discount=0.0,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Payment prepared successfully.",
            "payment": {
                "final_fare": trip.final_fare,
                "currency": trip.fare_currency,
                "fare_breakdown": trip.fare_breakdown,
                "payment_status": trip.payment_status,
                "supported_payment_methods": sorted(
                    SUPPORTED_PAYMENT_METHODS
                ),
                "pricing_inputs": {
                    "distance_km": (
                        fare_result["distance_km"]
                    ),
                    "duration_minutes": (
                        fare_result["duration_minutes"]
                    ),
                    "waiting_minutes": (
                        fare_result["waiting_minutes"]
                    ),
                },
            },
        }
    )


@app.route(
    "/api/trip/fare/finalize",
    methods=["POST"],
)
def finalize_trip_fare():
    """
    Calculate and store the final post-trip fare.
    """

    payload = request.get_json(silent=True) or {}

    try:
        distance_km = float(
            payload.get("distance_km", 4.0)
        )

        duration_minutes = float(
            payload.get("duration_minutes", 12.0)
        )

        waiting_minutes = float(
            payload.get("waiting_minutes", 0.0)
        )

        airport_fee = float(
            payload.get("airport_fee", 0.0)
        )

        toll_fee = float(
            payload.get("toll_fee", 0.0)
        )

        discount = float(
            payload.get("discount", 0.0)
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Valid numeric fare inputs are required."
                ),
            }
        ), 400

    trip = get_trip()

    try:
        fare_result = calculate_fare_breakdown(
            trip=trip,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            waiting_minutes=waiting_minutes,
            airport_fee=airport_fee,
            toll_fee=toll_fee,
            discount=discount,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Final fare calculated successfully.",
            "fare": fare_result,
            "payment_status": trip.payment_status,
        }
    )

@app.route(
    "/api/passenger/synchronization/updates",
    methods=["GET"],
)
def get_authenticated_passenger_synchronization_updates():
    """
    Return pending synchronization updates belonging
    to the authenticated Telegram Mini App passenger.

    Retrieval is non-destructive.

    The browser never supplies passenger_id directly.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        pending_updates = (
            get_pending_passenger_updates(
                passenger.passenger_id
            )
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    updates = [
        {
            "update_id": update.update_id,
            "event_id": update.event_id,
            "event_type": update.event_type,
            "entity": update.entity,
            "entity_id": update.entity_id,
            "targets": list(update.targets),
            "payload": dict(update.payload),
            "source": update.source,
            "version": update.version,
            "sequence": update.sequence,
            "created_at": (
                update.created_at.isoformat()
            ),
        }
        for update in pending_updates
    ]

    return jsonify(
        {
            "success": True,
            "passenger_id": passenger.passenger_id,
            "count": len(updates),
            "updates": updates,
        }
    )

@app.route(
    "/api/passenger/synchronization/updates/<update_id>/acknowledge",
    methods=["POST"],
)
def acknowledge_authenticated_passenger_synchronization_update(
    update_id,
):
    """
    Acknowledge one synchronization update belonging
    to the authenticated Telegram Mini App passenger.

    Authentication determines passenger identity.

    The browser supplies only the synchronization
    update ID. It cannot choose passenger_id.

    Passenger synchronization updates must be
    acknowledged in delivery order.

    A successful acknowledgement removes exactly one
    matching update and advances the authenticated
    passenger's synchronization cursor to that
    update's sequence.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        acknowledgement_result = (
            acknowledge_pending_passenger_update_in_order(
                passenger_id=passenger.passenger_id,
                update_id=update_id,
            )
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    if acknowledgement_result is None:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Pending synchronization update "
                    "not found for authenticated "
                    "passenger."
                ),
            }
        ), 404

    (
        acknowledged_update,
        synchronization_cursor,
    ) = acknowledgement_result

    return jsonify(
        {
            "success": True,
            "message": (
                "Passenger synchronization update "
                "acknowledged successfully."
            ),
            "passenger_id": (
                passenger.passenger_id
            ),
            "update": {
                "update_id": (
                    acknowledged_update.update_id
                ),
                "event_id": (
                    acknowledged_update.event_id
                ),
                "event_type": (
                    acknowledged_update.event_type
                ),
                "entity": (
                    acknowledged_update.entity
                ),
                "entity_id": (
                    acknowledged_update.entity_id
                ),
                "version": (
                    acknowledged_update.version
                ),
                "sequence": (
                    acknowledged_update.sequence
                ),
            },
            "cursor": {
                "passenger_id": (
                    synchronization_cursor.passenger_id
                ),
                "last_sequence": (
                    synchronization_cursor.last_sequence
                ),
                "updated_at": (
                    synchronization_cursor
                    .updated_at
                    .isoformat()
                ),
            },
        }
    )

@app.route(
    "/api/passenger/synchronization/recover",
    methods=["POST"],
)
def recover_authenticated_passenger_synchronization():
    """
    Recover the authenticated passenger's Mini App
    synchronization state.

    Recovery reconciles the Mini App Trip with the
    authoritative canonical Ride lifecycle and returns
    still-pending passenger synchronization updates.

    Passenger identity comes only from authenticated
    Telegram Mini App init data.

    Recovery never acknowledges pending updates.
    """

    trip = get_trip()

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        recovery_result = (
            recover_passenger_synchronization(
                trip=trip,
                passenger_id=passenger.passenger_id,
            )
        )
    except (
        MiniAppPassengerSynchronizationRecoveryError
    ) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    pending_updates = [
        {
            "update_id": update.update_id,
            "event_id": update.event_id,
            "event_type": update.event_type,
            "entity": update.entity,
            "entity_id": update.entity_id,
            "targets": list(update.targets),
            "payload": dict(update.payload),
            "source": update.source,
            "version": update.version,
            "created_at": (
                update.created_at.isoformat()
            ),
        }
        for update in recovery_result.pending_updates
    ]

    return jsonify(
        {
            "success": True,
            "message": (
                "Passenger synchronization recovery "
                "completed successfully."
            ),
            "recovery": {
                "passenger_id": (
                    recovery_result.passenger_id
                ),
                "canonical_ride_id": (
                    recovery_result.ride_id
                ),
                "canonical_driver_id": (
                    recovery_result.driver_id
                ),
                "canonical_state": (
                    recovery_result.canonical_state
                ),
                "previous_booking_status": (
                    recovery_result
                    .previous_presentation_status
                ),
                "booking_status": (
                    recovery_result.presentation_status
                ),
                "synchronized": (
                    recovery_result.synchronized
                ),
                "pending_update_count": (
                    len(pending_updates)
                ),
                "pending_updates": pending_updates,
            },
        }
    )

@app.route(
    "/api/passenger/synchronization/resume",
    methods=["POST"],
)
def resume_authenticated_passenger_synchronization():
    """
    Resume the authenticated passenger's Mini App
    synchronization state from the trusted server-side
    synchronization cursor.

    Passenger identity comes only from authenticated
    Telegram Mini App init data.

    Resume reconciles Mini App presentation with the
    authoritative canonical Ride lifecycle and returns
    pending synchronization updates occurring strictly
    after the passenger's last acknowledged sequence.

    Resume is non-destructive.

    It never acknowledges updates, never advances the
    synchronization cursor, and never transitions
    canonical Ride state.
    """

    trip = get_trip()

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    try:
        resume_result = (
            resume_passenger_synchronization(
                trip=trip,
                passenger_id=(
                    passenger.passenger_id
                ),
            )
        )
    except (
        MiniAppPassengerSynchronizationResumeError
    ) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    pending_updates = [
        {
            "update_id": update.update_id,
            "event_id": update.event_id,
            "event_type": update.event_type,
            "entity": update.entity,
            "entity_id": update.entity_id,
            "targets": list(update.targets),
            "payload": dict(update.payload),
            "source": update.source,
            "version": update.version,
            "sequence": update.sequence,
            "created_at": (
                update.created_at.isoformat()
            ),
        }
        for update in resume_result.pending_updates
    ]

    return jsonify(
        {
            "success": True,
            "message": (
                "Passenger synchronization resumed "
                "successfully."
            ),
            "resume": {
                "passenger_id": (
                    resume_result.passenger_id
                ),
                "canonical_ride_id": (
                    resume_result.ride_id
                ),
                "canonical_driver_id": (
                    resume_result.driver_id
                ),
                "canonical_state": (
                    resume_result.canonical_state
                ),
                "previous_booking_status": (
                    resume_result
                    .previous_presentation_status
                ),
                "booking_status": (
                    resume_result.presentation_status
                ),
                "synchronized": (
                    resume_result.synchronized
                ),
                "cursor": {
                    "last_acknowledged_sequence": (
                        resume_result
                        .last_acknowledged_sequence
                    ),
                    "updated_at": (
                        resume_result
                        .cursor
                        .updated_at
                        .isoformat()
                    ),
                },
                "replay_from_sequence": (
                    resume_result.replay_from_sequence
                ),
                "latest_available_sequence": (
                    resume_result
                    .latest_available_sequence
                ),
                "caught_up": (
                    resume_result.caught_up
                ),
                "pending_update_count": (
                    resume_result.pending_update_count
                ),
                "pending_updates": (
                    pending_updates
                ),
            },
        }
    )

@app.route(
    "/api/passenger/synchronization/replay",
    methods=["GET"],
)
def get_authenticated_passenger_synchronization_replay():
    """
    Return pending synchronization updates occurring
    strictly after one synchronization sequence for the
    authenticated Telegram Mini App passenger.

    Passenger identity comes only from Telegram
    authentication.

    Replay is non-destructive.
    """

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    after_sequence_raw = request.args.get(
        "after_sequence",
        "0",
    )

    try:
        after_sequence = int(
            after_sequence_raw
        )
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": (
                    "after_sequence must be a "
                    "non-negative integer."
                ),
            }
        ), 400

    try:
        replay_updates = (
            get_pending_passenger_updates_after_sequence(
                passenger_id=passenger.passenger_id,
                after_sequence=after_sequence,
            )
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    updates = [
        {
            "update_id": update.update_id,
            "event_id": update.event_id,
            "event_type": update.event_type,
            "entity": update.entity,
            "entity_id": update.entity_id,
            "targets": list(update.targets),
            "payload": dict(update.payload),
            "source": update.source,
            "version": update.version,
            "sequence": update.sequence,
            "created_at": (
                update.created_at.isoformat()
            ),
        }
        for update in replay_updates
    ]

    return jsonify(
        {
            "success": True,
            "passenger_id": passenger.passenger_id,
            "after_sequence": after_sequence,
            "count": len(updates),
            "updates": updates,
        }
    )

@app.route(
    "/api/trip/synchronize",
    methods=["POST"],
)
def synchronize_active_trip():
    """
    Synchronize the active Mini App Trip with the
    authoritative HABESHAGO Ride lifecycle.

    The caller is authenticated through Telegram
    Mini App init data.

    The browser never supplies ride_id,
    passenger_id, or driver_id directly.

    This endpoint is read-only with respect to the
    canonical Ride Platform. It may repair only the
    Mini App presentation state.
    """

    trip = get_trip()

    init_data = request.headers.get(
        "X-Telegram-Init-Data",
        "",
    )

    if not init_data:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Telegram Mini App authentication "
                    "data is required."
                ),
            }
        ), 401

    try:
        passenger = (
            authenticate_mini_app_passenger(
                init_data=init_data,
                bot_token=BOT_TOKEN,
            )
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 401

    if (
        trip.canonical_passenger_id
        != passenger.passenger_id
    ):
        return jsonify(
            {
                "success": False,
                "error": (
                    "Authenticated passenger does not "
                    "match the Mini App Trip."
                ),
            }
        ), 403

    try:
        synchronization_result = (
            synchronize_trip_with_canonical_ride(
                trip=trip,
            )
        )
    except MiniAppRideStateSynchronizationError as exc:
        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": (
                "Trip synchronized with canonical "
                "Ride state."
            ),
            "trip": {
                "canonical_ride_id": (
                    synchronization_result.ride_id
                ),
                "canonical_passenger_id": (
                    trip.canonical_passenger_id
                ),
                "canonical_driver_id": (
                    trip.canonical_driver_id
                ),
                "canonical_state": (
                    synchronization_result.canonical_state
                ),
                "previous_booking_status": (
                    synchronization_result
                    .previous_presentation_status
                ),
                "booking_status": (
                    synchronization_result
                    .presentation_status
                ),
                "synchronized": (
                    synchronization_result.synchronized
                ),
            },
        }
    )

@app.route(
    "/api/trip/payment/method",
    methods=["POST"],
)
def choose_trip_payment_method():
    """
    Store the passenger's selected payment method.
    """

    payload = request.get_json(silent=True) or {}

    payment_method = str(
        payload.get("payment_method", "")
    ).strip().lower()

    trip = get_trip()

    try:
        select_payment_method(
            trip=trip,
            payment_method=payment_method,
        )
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "supported_methods": sorted(
                    SUPPORTED_PAYMENT_METHODS
                ),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Payment method selected.",
            "payment": {
                "payment_method": trip.payment_method,
                "payment_status": trip.payment_status,
                "final_fare": trip.final_fare,
                "currency": trip.fare_currency,
            },
        }
    )

@app.route("/payment")
def payment_page():
    """
    Render the HABESHAGO Payment page.
    """

    page = get_payment_page()

    return render_template(
        "payment.html",
        page=page,
        active_page="home",
    )

@app.route(
    "/api/trip/payment/process",
    methods=["POST"],
)
def process_trip_payment():
    """
    Process the selected payment method and create
    a receipt-ready transaction record.
    """

    trip = get_trip()

    try:
        process_payment(trip)
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
            }
        ), 409

    return jsonify(
        {
            "success": True,
            "message": "Payment completed successfully.",
            "payment": {
                "payment_method": trip.payment_method,
                "payment_status": trip.payment_status,
                "final_fare": trip.final_fare,
                "currency": trip.fare_currency,
                "payment_transaction_id": (
                    trip.payment_transaction_id
                ),
                "receipt_id": trip.receipt_id,
                "payment_completed_at": (
                    trip.payment_completed_at
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