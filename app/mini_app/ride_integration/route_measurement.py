"""
HABESHAGO Mini App Route Measurement Contract

Defines authoritative route facts required by the
shared Ride Offer Platform.

This module does not calculate routes itself.

A future routing provider or platform service must
produce these measurements.
"""

from dataclasses import dataclass
from math import isfinite


class MiniAppRouteMeasurementError(ValueError):
    """
    Raised when route measurements are invalid.
    """


def _require_positive_number(
    value: int | float,
    *,
    field_name: str,
) -> float:
    """
    Require one finite positive numeric value.
    """

    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise MiniAppRouteMeasurementError(
            f"{field_name} must be a positive number."
        )

    normalized = float(
        value
    )

    if (
        not isfinite(normalized)
        or normalized <= 0.0
    ):
        raise MiniAppRouteMeasurementError(
            f"{field_name} must be a positive number."
        )

    return normalized


@dataclass(frozen=True)
class MiniAppRouteMeasurement:
    """
    Immutable authoritative measurement of one planned
    passenger journey.

    distance_km:
        Road-network or otherwise authoritative trip
        distance.

    duration_minutes:
        Authoritative planned trip duration.

    provider:
        Name of the routing source that produced the
        measurement.

    measurement_reference:
        Optional provider/platform reference allowing the
        measurement to be traced later.
    """

    distance_km: float
    duration_minutes: float
    provider: str
    measurement_reference: str | None = None

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "distance_km",
            _require_positive_number(
                self.distance_km,
                field_name="distance_km",
            ),
        )

        object.__setattr__(
            self,
            "duration_minutes",
            _require_positive_number(
                self.duration_minutes,
                field_name="duration_minutes",
            ),
        )

        if (
            not isinstance(
                self.provider,
                str,
            )
            or not self.provider.strip()
        ):
            raise MiniAppRouteMeasurementError(
                "provider must be non-empty text."
            )

        object.__setattr__(
            self,
            "provider",
            self.provider.strip(),
        )

        if (
            self.measurement_reference
            is not None
        ):
            if (
                not isinstance(
                    self.measurement_reference,
                    str,
                )
                or not self.measurement_reference.strip()
            ):
                raise MiniAppRouteMeasurementError(
                    (
                        "measurement_reference must be "
                        "non-empty text when provided."
                    )
                )

            object.__setattr__(
                self,
                "measurement_reference",
                self.measurement_reference.strip(),
            )