import logging
import time
from functools import lru_cache

import requests


logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

USER_AGENT = (
    "HABESHAGO/1.0 "
    "(Ethiopia ride-hailing development; "
    "contact: contact@habeshago.et)"
)


def format_coordinates(latitude, longitude):
    """
    Return coordinates in a consistent display format.
    """

    return f"{latitude:.6f}, {longitude:.6f}"


def is_meaningful_name(value):
    """
    Return True when a value contains at least
    one letter or number.
    """

    if not value:
        return False

    value = str(value).strip()

    return bool(value) and any(
        character.isalnum()
        for character in value
    )


def clean_city_name(value):
    """
    Normalize multilingual Addis Ababa labels
    into a clean English display name.
    """

    if not value:
        return ""

    value = str(value).strip()

    if "Addis Ababa" in value:
        return "Addis Ababa"

    return value


def clean_country_name(value):
    """
    Normalize Ethiopia's country name for
    internal full-address formatting.
    """

    if not value:
        return ""

    value = str(value).strip()

    if value.casefold() in {
        "ethiopia",
        "ኢትዮጵያ",
    }:
        return "Ethiopia"

    return value


@lru_cache(maxsize=5000)
def _reverse_geocode_cached(
    latitude,
    longitude,
    language,
):
    """
    Perform and cache one Nominatim
    reverse-geocoding request.
    """

    response = requests.get(
        NOMINATIM_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
            "namedetails": 1,
            "accept-language": language,
        },
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_location_details(
    latitude,
    longitude,
    language="en",
):
    """
    Convert coordinates into short and full
    human-readable location names.

    Example result:

        {
            "short": "Nefas Silk, Addis Ababa",
            "full": "Nefas Silk, Addis Ababa, Ethiopia",
            "latitude": 8.95855,
            "longitude": 38.77134,
        }
    """

    rounded_latitude = round(
        float(latitude),
        5,
    )

    rounded_longitude = round(
        float(longitude),
        5,
    )

    fallback = format_coordinates(
        rounded_latitude,
        rounded_longitude,
    )

    last_error = None

    for attempt in range(2):
        try:
            data = _reverse_geocode_cached(
                rounded_latitude,
                rounded_longitude,
                language,
            )

            # Nominatim may return None for these fields,
            # so "or {}" is required.
            address = data.get("address") or {}
            namedetails = data.get("namedetails") or {}

            top_level_name = (
                data.get("name") or ""
            ).strip()

            localized_name = (
                namedetails.get(
                    f"name:{language}"
                )
                or namedetails.get("name")
                or ""
            )

            # Prefer landmarks and familiar local areas
            # before roads, cities, or larger districts.
            preferred_values = (
                top_level_name,
                localized_name,
                address.get("amenity"),
                address.get("tourism"),
                address.get("shop"),
                address.get("office"),
                address.get("aeroway"),
                address.get("railway"),
                address.get("building"),
                address.get("residential"),
                address.get("locality"),
                address.get("hamlet"),
                address.get("city_block"),
                address.get("neighbourhood"),
                address.get("quarter"),
                address.get("suburb"),
                address.get("borough"),
                address.get("city_district"),
                address.get("county"),
                address.get("road"),
                address.get("village"),
                address.get("town"),
                address.get("city"),
                address.get("state_district"),
            )

            primary_name = next(
                (
                    str(value).strip()
                    for value in preferred_values
                    if is_meaningful_name(value)
                ),
                fallback,
            )

            city_name = clean_city_name(
                address.get("city")
                or address.get("town")
                or address.get("municipality")
                or address.get("state_district")
                or address.get("state")
            )

            country_name = clean_country_name(
                address.get("country")
            )

            # Create the short Telegram display name.
            if (
                is_meaningful_name(primary_name)
                and is_meaningful_name(city_name)
                and primary_name.casefold()
                != city_name.casefold()
            ):
                short_name = (
                    f"{primary_name}, {city_name}"
                )
            else:
                short_name = (
                    primary_name
                    if is_meaningful_name(
                        primary_name
                    )
                    else city_name
                )

            if not is_meaningful_name(
                short_name
            ):
                short_name = fallback

            # Keep a clean full location internally
            # for future receipts, history and support.
            full_parts = []

            for part in (
                primary_name,
                city_name,
                country_name,
            ):
                if not is_meaningful_name(part):
                    continue

                if any(
                    part.casefold()
                    == existing.casefold()
                    for existing in full_parts
                ):
                    continue

                full_parts.append(part)

            full_name = ", ".join(full_parts)

            if not is_meaningful_name(full_name):
                display_name = (
                    data.get("display_name")
                    or ""
                ).strip()

                full_name = (
                    display_name
                    if is_meaningful_name(
                        display_name
                    )
                    else short_name
                )

            return {
                "short": short_name,
                "full": full_name,
                "latitude": rounded_latitude,
                "longitude": rounded_longitude,
            }

        except requests.RequestException as error:
            last_error = error

            logger.warning(
                (
                    "Reverse geocoding attempt %s "
                    "failed for %s, %s: %s"
                ),
                attempt + 1,
                rounded_latitude,
                rounded_longitude,
                error,
            )

            if attempt == 0:
                time.sleep(0.5)

        except (
            TypeError,
            ValueError,
            KeyError,
            AttributeError,
        ) as error:
            last_error = error

            logger.error(
                (
                    "Invalid geocoding response "
                    "for %s, %s: %s"
                ),
                rounded_latitude,
                rounded_longitude,
                error,
            )

            break

    logger.warning(
        (
            "Using coordinate fallback for "
            "%s, %s after error: %s"
        ),
        rounded_latitude,
        rounded_longitude,
        last_error,
    )

    return {
        "short": fallback,
        "full": fallback,
        "latitude": rounded_latitude,
        "longitude": rounded_longitude,
    }


def get_location_name(
    latitude,
    longitude,
    language="en",
):
    """
    Return only the short location name
    for Telegram messages.
    """

    location = get_location_details(
        latitude,
        longitude,
        language,
    )

    return location["short"]