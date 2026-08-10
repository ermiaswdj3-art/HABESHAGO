"""
HABESHAGO Ride Commerce Orchestration Domain

Defines the immutable result of one operational
Ride -> Pricing -> Commerce workflow.

This domain joins:
- Ride Commerce operational context
- Authoritative Pricing workflow
- Commerce payment preparation

It does not:
- calculate fares
- calculate commission
- calculate driver earnings
- modify Pricing authority
- execute payment providers
- verify payments
- reconcile payments
"""

from dataclasses import (
    dataclass,
)

from app.commerce.orchestration import (
    CommerceOrchestrationResult,
)

from app.pricing.workflow import (
    PricingWorkflowResult,
)

from app.ride_commerce.context import (
    RideCommerceContext,
)


class RideCommerceStatus:
    """
    Canonical Ride Commerce workflow states.
    """

    PAYMENT_PREPARED = "payment_prepared"

    ALL = {
        PAYMENT_PREPARED,
    }


@dataclass(
    frozen=True,
    slots=True,
)
class RideCommerceOrchestrationResult:
    """
    Immutable result joining one canonical ride context
    to authoritative Pricing and Commerce results.
    """

    context: RideCommerceContext

    pricing_workflow: PricingWorkflowResult

    commerce_result: CommerceOrchestrationResult

    status: str

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.context,
            RideCommerceContext,
        ):
            raise ValueError(
                (
                    "context must be a "
                    "RideCommerceContext."
                )
            )

        if not isinstance(
            self.pricing_workflow,
            PricingWorkflowResult,
        ):
            raise ValueError(
                (
                    "pricing_workflow must be a "
                    "PricingWorkflowResult."
                )
            )

        if not isinstance(
            self.commerce_result,
            CommerceOrchestrationResult,
        ):
            raise ValueError(
                (
                    "commerce_result must be a "
                    "CommerceOrchestrationResult."
                )
            )

        if (
            self.status
            not in RideCommerceStatus.ALL
        ):
            raise ValueError(
                (
                    "Unsupported Ride Commerce status: "
                    f"{self.status}"
                )
            )

        if (
            self.commerce_result.pricing_workflow
            != self.pricing_workflow
        ):
            raise ValueError(
                (
                    "Commerce result must use the same "
                    "authoritative Pricing workflow."
                )
            )

        if (
            self.commerce_result
            .payment_obligation
            .source_reference
            != str(
                self.context.ride_id
            )
        ):
            raise ValueError(
                (
                    "Payment obligation must reference "
                    "the canonical ride_id."
                )
            )

        if (
            self.commerce_result
            .payment_workflow
            .payment_request
            .payer_id
            != self.context.passenger_id
        ):
            raise ValueError(
                (
                    "Payment payer must match the "
                    "canonical ride passenger."
                )
            )

        if (
            self.commerce_result
            .payment_workflow
            .payment_request
            .payment_method
            != self.context.payment_method
        ):
            raise ValueError(
                (
                    "Payment method must match the "
                    "Ride Commerce context."
                )
            )