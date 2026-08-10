"""
HABESHAGO Mini App Ride Integration

Public integration boundary connecting Mini App
presentation state to the authoritative shared
HABESHAGO Ride Platform.

The Mini App does not create or redefine canonical
Ride identity, pricing authority, or Ride lifecycle
state through this package.
"""

from app.mini_app.ride_integration.acceptance_adapter import (
    attach_trip_from_accepted_offer,
)

from app.mini_app.ride_integration.binder import (
    bind_canonical_ride_reference,
)

from app.mini_app.ride_integration.lifecycle_bridge import (
    MiniAppRideLifecycleBridgeError,
    MiniAppRideLifecycleResult,
    accept_offer_and_bind_trip,
)

from app.mini_app.ride_integration.models import (
    MiniAppCanonicalRideReference,
)

from app.mini_app.ride_integration.offer_orchestrator import (
    MiniAppRideOfferOrchestrationResult,
    MiniAppRideOfferOrchestratorError,
    orchestrate_mini_app_ride_offer,
)

from app.mini_app.ride_integration.offer_preparation import (
    MiniAppRideOfferPreparationError,
    prepare_ride_offer_context,
)

from app.mini_app.ride_integration.pricing_adapter import (
    MiniAppPricingAdapterError,
    MiniAppPricingResult,
    price_mini_app_ride,
)

from app.mini_app.ride_integration.reference_loader import (
    load_canonical_ride_reference,
)

from app.mini_app.ride_integration.ride_offer_adapter import (
    MiniAppRideOfferAdapterError,
    create_canonical_ride_offer,
)

from app.mini_app.ride_integration.ride_offer_context import (
    MiniAppRideOfferContext,
    MiniAppRideOfferContextError,
)

from app.mini_app.ride_integration.route_context import (
    MiniAppRouteContext,
    MiniAppRouteContextError,
    build_route_context,
)

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
    MiniAppRouteMeasurementError,
)

from app.mini_app.ride_integration.route_measurement_adapter import (
    MiniAppRouteMeasurementAdapterError,
    measure_mini_app_route,
)

from app.mini_app.ride_integration.service import (
    MiniAppRideIntegrationResult,
    attach_trip_to_canonical_ride,
)


__all__ = [
    "MiniAppCanonicalRideReference",
    "MiniAppPricingAdapterError",
    "MiniAppPricingResult",
    "MiniAppRideIntegrationResult",
    "MiniAppRideLifecycleBridgeError",
    "MiniAppRideLifecycleResult",
    "MiniAppRideOfferAdapterError",
    "MiniAppRideOfferContext",
    "MiniAppRideOfferContextError",
    "MiniAppRideOfferOrchestrationResult",
    "MiniAppRideOfferOrchestratorError",
    "MiniAppRideOfferPreparationError",
    "MiniAppRouteContext",
    "MiniAppRouteContextError",
    "MiniAppRouteMeasurement",
    "MiniAppRouteMeasurementError",
    "accept_offer_and_bind_trip",
    "attach_trip_from_accepted_offer",
    "attach_trip_to_canonical_ride",
    "bind_canonical_ride_reference",
    "build_route_context",
    "create_canonical_ride_offer",
    "load_canonical_ride_reference",
    "orchestrate_mini_app_ride_offer",
    "prepare_ride_offer_context",
    "MiniAppRouteMeasurementAdapterError",
    "measure_mini_app_route",
    "price_mini_app_ride",
]