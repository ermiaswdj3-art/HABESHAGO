"""
HABESHAGO Mini App Production Runtime

Starts the HABESHAGO Mini App through Waitress using
deployment-friendly host and port configuration.

Commit #115 purpose:

- bind the Mini App to a deployment-accessible host;
- respect the PORT supplied by cloud platforms;
- preserve safe local defaults;
- expose one provider-neutral production start contract.

TLS/HTTPS termination remains the responsibility of the
deployment platform or reverse proxy.
"""

import os

from waitress import serve

from app.mini_app.wsgi import application


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080


def get_runtime_host() -> str:
    """
    Return the configured Mini App runtime host.
    """

    host = os.getenv(
        "HABESHAGO_HOST",
        DEFAULT_HOST,
    ).strip()

    return host or DEFAULT_HOST


def get_runtime_port() -> int:
    """
    Return the configured Mini App runtime port.

    Cloud platforms commonly provide PORT dynamically.
    HABESHAGO_PORT remains available as an explicit
    application-specific override.
    """

    raw_port = (
        os.getenv("HABESHAGO_PORT")
        or os.getenv("PORT")
        or str(DEFAULT_PORT)
    )

    try:
        port = int(raw_port)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Mini App runtime port must be an integer."
        ) from exc

    if not 1 <= port <= 65535:
        raise ValueError(
            (
                "Mini App runtime port must be "
                "between 1 and 65535."
            )
        )

    return port


def run() -> None:
    """
    Start the HABESHAGO Mini App through Waitress.
    """

    host = get_runtime_host()
    port = get_runtime_port()

    print(
        (
            "Starting HABESHAGO Mini App "
            f"on {host}:{port}"
        )
    )

    serve(
        application,
        host=host,
        port=port,
    )


if __name__ == "__main__":
    run()