"""
HABESHAGO Admin Driver Action State

Manages temporary Telegram workflow state while an
administrator prepares, confirms, or cancels a driver
administration action.

Persistent driver state remains authoritative in SQLite.
This module stores only short-lived interface context.
"""


PENDING_DRIVER_ADMIN_ACTION_KEY = (
    "pending_driver_admin_action"
)


STAGE_AWAITING_REASON = (
    "awaiting_reason"
)

STAGE_AWAITING_CONFIRMATION = (
    "awaiting_confirmation"
)


VALID_WORKFLOW_STAGES = {
    STAGE_AWAITING_REASON,
    STAGE_AWAITING_CONFIRMATION,
}


def set_pending_driver_admin_action(
    user_data: dict,
    *,
    driver_id: int,
    action: str,
    stage: str,
    reason: str | None = None,
) -> dict:
    """
    Store and return one pending administration workflow.
    """

    if stage not in VALID_WORKFLOW_STAGES:
        raise ValueError(
            "Invalid driver administration "
            "workflow stage."
        )

    pending_action = {
        "driver_id": int(driver_id),
        "action": str(action).strip().upper(),
        "stage": stage,
        "reason": (
            str(reason).strip()
            if reason is not None
            else None
        ),
    }

    user_data[
        PENDING_DRIVER_ADMIN_ACTION_KEY
    ] = pending_action

    return pending_action


def get_pending_driver_admin_action(
    user_data: dict,
) -> dict | None:
    """
    Return the current temporary administration workflow.
    """

    pending_action = user_data.get(
        PENDING_DRIVER_ADMIN_ACTION_KEY
    )

    if not isinstance(
        pending_action,
        dict,
    ):
        return None

    return pending_action


def update_pending_driver_admin_reason(
    user_data: dict,
    reason: str,
) -> dict:
    """
    Store the administrator reason and advance the workflow
    to confirmation.
    """

    pending_action = (
        get_pending_driver_admin_action(
            user_data
        )
    )

    if pending_action is None:
        raise ValueError(
            "No pending driver administration "
            "action exists."
        )

    normalized_reason = str(
        reason or ""
    ).strip()

    if not normalized_reason:
        raise ValueError(
            "An administration reason is required."
        )

    pending_action["reason"] = (
        normalized_reason
    )

    pending_action["stage"] = (
        STAGE_AWAITING_CONFIRMATION
    )

    return pending_action


def clear_pending_driver_admin_action(
    user_data: dict,
) -> None:
    """
    Remove any temporary driver administration workflow.
    """

    user_data.pop(
        PENDING_DRIVER_ADMIN_ACTION_KEY,
        None,
    )


def is_awaiting_driver_admin_reason(
    user_data: dict,
) -> bool:
    """
    Return True when Telegram should interpret the next
    administrator text message as an action reason.
    """

    pending_action = (
        get_pending_driver_admin_action(
            user_data
        )
    )

    return (
        pending_action is not None
        and pending_action.get("stage")
        == STAGE_AWAITING_REASON
    )