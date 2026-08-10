"""
HABESHAGO Ride Commerce Platform

Production integration boundary joining the operational
Ride Platform with authoritative Pricing and Commerce
platform capabilities.

This package does not calculate fares, commissions,
driver earnings, or payment amounts independently.

Authoritative financial values originate from the
Pricing Platform and flow into Commerce without
recalculation.
"""

from app.ride_commerce.context import (
    RideCommerceContext,
)

from app.ride_commerce.context_loader import (
    load_ride_commerce_context,
)

from app.ride_commerce.orchestration import (
    RideCommerceOrchestrationResult,
    RideCommerceStatus,
)

from app.ride_commerce.orchestrator import (
    prepare_ride_commerce_payment,
)


__all__ = [
    "RideCommerceContext",
    "RideCommerceOrchestrationResult",
    "RideCommerceStatus",
    "load_ride_commerce_context",
    "prepare_ride_commerce_payment",
]