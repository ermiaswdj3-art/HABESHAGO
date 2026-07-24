from datetime import datetime, timedelta


# Stores the last execution time
# for important user actions.
_last_actions = {}

# Ignore duplicate actions received
# within this many seconds.
ACTION_WINDOW_SECONDS = 3


def is_duplicate_action(
    user_id,
    action_name,
):
    """
    Return True if the same user has
    already performed the same action
    within the protection window.
    """

    now = datetime.now()

    key = (
        user_id,
        action_name,
    )

    if key in _last_actions:

        previous = _last_actions[key]

        if (
            now - previous
            < timedelta(
                seconds=ACTION_WINDOW_SECONDS
            )
        ):
            return True

    _last_actions[key] = now

    return False