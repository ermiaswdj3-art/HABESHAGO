"""
HABESHAGO Driver Administration Service

Defines the canonical business rules for driver
administration across Telegram Admin, future Web Admin,
future native clients, and authorized platform APIs.

Administrative interfaces must call this service rather
than changing driver or vehicle records directly.
"""

from app.constants.driver_admin_actions import (
    DriverAdminAction,
)

from app.database.driver_administration_repository import (
    apply_driver_admin_transition,
    get_driver_admin_actions,
    get_driver_management_record,
    list_driver_management_records,
)


REGISTRATION_VERIFICATION_PENDING = (
    "verification_pending"
)

REGISTRATION_APPROVED = "approved"

REGISTRATION_REJECTED = "rejected"

REGISTRATION_SUSPENDED = "suspended"


VERIFICATION_PENDING = "pending"

VERIFICATION_VERIFIED = "verified"

VERIFICATION_REJECTED = "rejected"


OPERATIONAL_OFFLINE = "offline"


def _validate_actor_id(
    actor_id: int,
) -> int:
    """
    Validate and return the administrator identity.
    """

    try:
        normalized_actor_id = int(
            actor_id
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            "A valid administrator ID is required."
        ) from error

    if normalized_actor_id <= 0:
        raise ValueError(
            "A valid administrator ID is required."
        )

    return normalized_actor_id


def _normalize_reason(
    reason: str | None,
    *,
    required: bool,
) -> str | None:
    """
    Clean and validate an administration reason.
    """

    normalized_reason = str(
        reason or ""
    ).strip()

    if required and not normalized_reason:
        raise ValueError(
            "A reason is required for this "
            "administrative action."
        )

    if not normalized_reason:
        return None

    if len(normalized_reason) > 1000:
        raise ValueError(
            "Administration reason is too long."
        )

    return normalized_reason


def _require_driver(
    driver_id: int,
) -> dict:
    """
    Return the canonical driver-management record.

    Raise ValueError when the driver does not exist.
    """

    try:
        normalized_driver_id = int(
            driver_id
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            "A valid driver ID is required."
        ) from error

    record = get_driver_management_record(
        normalized_driver_id
    )

    if record is None:
        raise ValueError(
            "Driver profile not found."
        )

    return record


def _require_active_vehicle(
    record: dict,
) -> dict:
    """
    Return the active vehicle or reject the transition.
    """

    active_vehicle = record.get(
        "active_vehicle"
    )

    if active_vehicle is None:
        raise ValueError(
            "Driver has no active vehicle."
        )

    if not active_vehicle["is_active"]:
        raise ValueError(
            "Driver has no active operational vehicle."
        )

    return active_vehicle


def _build_transition_result(
    *,
    audit_action: dict,
) -> dict:
    """
    Build the shared result returned after a transition.
    """

    updated_driver = (
        get_driver_management_record(
            audit_action["driver_id"]
        )
    )

    if updated_driver is None:
        raise RuntimeError(
            "Updated driver record could not be loaded."
        )

    return {
        "success": True,
        "action": audit_action,
        "driver": updated_driver,
    }


def get_managed_driver(
    driver_id: int,
) -> dict | None:
    """
    Return one canonical driver-management profile.
    """

    try:
        normalized_driver_id = int(
            driver_id
        )

    except (TypeError, ValueError):
        return None

    record = get_driver_management_record(
        normalized_driver_id
    )

    if record is None:
        return None

    return {
        **record,
        "administration_history": (
            get_driver_admin_actions(
                normalized_driver_id
            )
        ),
    }


def list_managed_drivers(
    *,
    registration_status: str | None = None,
    operational_status: str | None = None,
) -> list[dict]:
    """
    Return drivers with optional canonical filters.
    """

    records = (
        list_driver_management_records()
    )

    if registration_status is not None:
        normalized_registration_status = str(
            registration_status
        ).strip()

        records = [
            record
            for record in records
            if record["registration_status"]
            == normalized_registration_status
        ]

    if operational_status is not None:
        normalized_operational_status = str(
            operational_status
        ).strip()

        records = [
            record
            for record in records
            if record["operational_status"]
            == normalized_operational_status
        ]

    return records


def approve_driver(
    *,
    driver_id: int,
    actor_id: int,
    reason: str | None = None,
) -> dict:
    """
    Approve one pending driver application.

    Approval verifies the driver's identity and active
    vehicle but leaves the driver offline. The driver
    must voluntarily go online afterward.
    """

    actor_id = _validate_actor_id(
        actor_id
    )

    record = _require_driver(
        driver_id
    )

    _require_active_vehicle(
        record
    )

    if (
        record["registration_status"]
        != REGISTRATION_VERIFICATION_PENDING
    ):
        raise ValueError(
            "Only a verification-pending driver "
            "may be approved."
        )

    normalized_reason = _normalize_reason(
        reason,
        required=False,
    )

    audit_action = (
        apply_driver_admin_transition(
            driver_id=record["driver_id"],
            actor_id=actor_id,
            action_type=(
                DriverAdminAction.APPROVE
            ),
            new_registration_status=(
                REGISTRATION_APPROVED
            ),
            new_identity_status=(
                VERIFICATION_VERIFIED
            ),
            new_vehicle_status=(
                VERIFICATION_VERIFIED
            ),
            new_operational_status=(
                OPERATIONAL_OFFLINE
            ),
            reason=normalized_reason,
            update_verified_at=True,
        )
    )

    return _build_transition_result(
        audit_action=audit_action
    )


def reject_driver(
    *,
    driver_id: int,
    actor_id: int,
    reason: str,
) -> dict:
    """
    Reject one pending driver application.

    Rejection requires an explanation and forces the
    driver fully offline.
    """

    actor_id = _validate_actor_id(
        actor_id
    )

    record = _require_driver(
        driver_id
    )

    _require_active_vehicle(
        record
    )

    if (
        record["registration_status"]
        != REGISTRATION_VERIFICATION_PENDING
    ):
        raise ValueError(
            "Only a verification-pending driver "
            "may be rejected."
        )

    normalized_reason = _normalize_reason(
        reason,
        required=True,
    )

    audit_action = (
        apply_driver_admin_transition(
            driver_id=record["driver_id"],
            actor_id=actor_id,
            action_type=(
                DriverAdminAction.REJECT
            ),
            new_registration_status=(
                REGISTRATION_REJECTED
            ),
            new_identity_status=(
                VERIFICATION_REJECTED
            ),
            new_vehicle_status=(
                VERIFICATION_REJECTED
            ),
            new_operational_status=(
                OPERATIONAL_OFFLINE
            ),
            reason=normalized_reason,
            update_verified_at=False,
        )
    )

    return _build_transition_result(
        audit_action=audit_action
    )


def suspend_driver(
    *,
    driver_id: int,
    actor_id: int,
    reason: str,
) -> dict:
    """
    Suspend one approved driver.

    Suspension is blocked while the driver has a
    persistent active ride. Identity and vehicle
    verification remain preserved.
    """

    actor_id = _validate_actor_id(
        actor_id
    )

    record = _require_driver(
        driver_id
    )

    active_vehicle = _require_active_vehicle(
        record
    )

    if (
        record["registration_status"]
        != REGISTRATION_APPROVED
    ):
        raise ValueError(
            "Only an approved driver may be suspended."
        )

    if record["has_active_ride"]:
        raise ValueError(
            "Driver cannot be suspended while "
            "handling an active ride."
        )

    normalized_reason = _normalize_reason(
        reason,
        required=True,
    )

    audit_action = (
        apply_driver_admin_transition(
            driver_id=record["driver_id"],
            actor_id=actor_id,
            action_type=(
                DriverAdminAction.SUSPEND
            ),
            new_registration_status=(
                REGISTRATION_SUSPENDED
            ),
            new_identity_status=(
                record[
                    "identity_verification_status"
                ]
            ),
            new_vehicle_status=(
                active_vehicle[
                    "verification_status"
                ]
            ),
            new_operational_status=(
                OPERATIONAL_OFFLINE
            ),
            reason=normalized_reason,
            update_verified_at=False,
        )
    )

    return _build_transition_result(
        audit_action=audit_action
    )


def restore_driver(
    *,
    driver_id: int,
    actor_id: int,
    reason: str | None = None,
) -> dict:
    """
    Restore one suspended driver to approved status.

    Restoration preserves verified identity and vehicle
    status and leaves the driver offline.
    """

    actor_id = _validate_actor_id(
        actor_id
    )

    record = _require_driver(
        driver_id
    )

    active_vehicle = _require_active_vehicle(
        record
    )

    if (
        record["registration_status"]
        != REGISTRATION_SUSPENDED
    ):
        raise ValueError(
            "Only a suspended driver may be restored."
        )

    if (
        record["identity_verification_status"]
        != VERIFICATION_VERIFIED
    ):
        raise ValueError(
            "Driver identity must remain verified "
            "before restoration."
        )

    if (
        record["vehicle_verification_status"]
        != VERIFICATION_VERIFIED
        or active_vehicle[
            "verification_status"
        ]
        != VERIFICATION_VERIFIED
    ):
        raise ValueError(
            "The active vehicle must remain verified "
            "before restoration."
        )

    normalized_reason = _normalize_reason(
        reason,
        required=False,
    )

    audit_action = (
        apply_driver_admin_transition(
            driver_id=record["driver_id"],
            actor_id=actor_id,
            action_type=(
                DriverAdminAction.RESTORE
            ),
            new_registration_status=(
                REGISTRATION_APPROVED
            ),
            new_identity_status=(
                VERIFICATION_VERIFIED
            ),
            new_vehicle_status=(
                VERIFICATION_VERIFIED
            ),
            new_operational_status=(
                OPERATIONAL_OFFLINE
            ),
            reason=normalized_reason,
            update_verified_at=False,
        )
    )

    return _build_transition_result(
        audit_action=audit_action
    )


def resubmit_driver(
    *,
    driver_id: int,
    actor_id: int,
    reason: str | None = None,
) -> dict:
    """
    Return one rejected application to verification pending.

    Identity and active-vehicle verification are reset to
    pending, and the driver remains offline.
    """

    actor_id = _validate_actor_id(
        actor_id
    )

    record = _require_driver(
        driver_id
    )

    _require_active_vehicle(
        record
    )

    if (
        record["registration_status"]
        != REGISTRATION_REJECTED
    ):
        raise ValueError(
            "Only a rejected driver application "
            "may be resubmitted."
        )

    normalized_reason = _normalize_reason(
        reason,
        required=False,
    )

    audit_action = (
        apply_driver_admin_transition(
            driver_id=record["driver_id"],
            actor_id=actor_id,
            action_type=(
                DriverAdminAction.RESUBMIT
            ),
            new_registration_status=(
                REGISTRATION_VERIFICATION_PENDING
            ),
            new_identity_status=(
                VERIFICATION_PENDING
            ),
            new_vehicle_status=(
                VERIFICATION_PENDING
            ),
            new_operational_status=(
                OPERATIONAL_OFFLINE
            ),
            reason=normalized_reason,
            update_verified_at=False,
        )
    )

    return _build_transition_result(
        audit_action=audit_action
    )