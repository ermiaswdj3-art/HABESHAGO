"""
HABESHAGO Commerce Orchestration Domain

Defines the immutable boundary joining the authoritative
Pricing Platform to the Payment Platform.

Commerce coordinates the two platforms.

It does not:
- calculate fares
- allocate commission
- calculate driver earnings
- execute payment providers
- verify payment evidence
- reconcile payments
- modify Pricing authority
- modify Payment authority
"""

from dataclasses import (
    dataclass,
)

from app.payments.models import (
    PaymentObligation,
)

from app.payments.orchestration import (
    PaymentOrchestrationResult,
)

from app.pricing.workflow import (
    PricingWorkflowResult,
)


class CommerceWorkflowStatus:
    """
    Canonical Commerce workflow states.
    """

    PAYMENT_PREPARED = "payment_prepared"

    ALL = {
        PAYMENT_PREPARED,
    }


@dataclass(
    frozen=True,
    slots=True,
)
class CommerceOrchestrationResult:
    """
    Immutable result joining one completed Pricing
    workflow to one prepared Payment workflow.
    """

    pricing_workflow: PricingWorkflowResult

    payment_obligation: PaymentObligation

    payment_workflow: PaymentOrchestrationResult

    status: str

    def __post_init__(
        self,
    ) -> None:
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
            self.payment_obligation,
            PaymentObligation,
        ):
            raise ValueError(
                (
                    "payment_obligation must be a "
                    "PaymentObligation."
                )
            )

        if not isinstance(
            self.payment_workflow,
            PaymentOrchestrationResult,
        ):
            raise ValueError(
                (
                    "payment_workflow must be a "
                    "PaymentOrchestrationResult."
                )
            )

        if (
            self.status
            not in CommerceWorkflowStatus.ALL
        ):
            raise ValueError(
                (
                    "Unsupported Commerce workflow "
                    f"status: {self.status}"
                )
            )

        pricing = (
            self.pricing_workflow.pricing
        )

        allocation = (
            pricing.financial_allocation
        )

        if allocation is None:
            raise ValueError(
                (
                    "Commerce requires a Pricing "
                    "financial allocation."
                )
            )

        # ======================================
        # PRICING → PAYMENT AUTHORITY
        # ======================================

        if (
            self.payment_obligation.amount
            != allocation.passenger_fare
        ):
            raise ValueError(
                (
                    "Payment obligation amount must "
                    "exactly equal Pricing passenger "
                    "fare."
                )
            )

        if (
            self.payment_obligation.currency
            != allocation.currency
        ):
            raise ValueError(
                (
                    "Payment obligation currency must "
                    "match Pricing allocation currency."
                )
            )

        if (
            self.payment_obligation.pricing_quote_id
            != pricing.quote.quote_id
        ):
            raise ValueError(
                (
                    "Payment obligation must preserve "
                    "Pricing quote provenance."
                )
            )

        if (
            self.payment_obligation.pricing_request_id
            != pricing.request.request_id
        ):
            raise ValueError(
                (
                    "Payment obligation must preserve "
                    "Pricing request provenance."
                )
            )

        # ======================================
        # PAYMENT WORKFLOW LINKAGE
        # ======================================

        if (
            self.payment_workflow.obligation
            != self.payment_obligation
        ):
            raise ValueError(
                (
                    "Payment workflow must use the "
                    "Commerce payment obligation."
                )
            )

        if (
            self.payment_workflow.status
            != "prepared"
        ):
            raise ValueError(
                (
                    "Commerce payment preparation "
                    "requires a PREPARED Payment "
                    "workflow."
                )
            )