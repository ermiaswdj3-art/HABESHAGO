import logging
import time
from functools import lru_cache

import requests


logger = logging.getLogger(__name__)

NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/reverse"
)

USER_AGENT = (
    "HABESHAGO/1.0 "
    "(https://github.com/ermiaswdj3-art/HABESHAGO)"
)


def _clean_text(value):
    """
    Return normalized text or an empty string.
    """

    if value is None:
        return ""

    return " ".join(
        str(value).strip().split()
    )


def format_coordinates(
    latitude,
    longitude,
):
    """
    Return coordinates in a consistent
    display format.
    """

    return (
        f"{latitude:.6f}, "
        f"{longitude:.6f}"
    )


def is_meaningful_name(value):
    """
    Return True when a value contains
    at least one letter or number.
    """

    clean_value = _clean_text(
        value
    )

    if not clean_value:
        return False

    return any(
        character.isalnum()
        for character in clean_value
    )


def clean_city_name(value):
    """
    Normalize multilingual Addis Ababa labels
    into a clean English city name.
    """

    city_name = _clean_text(
        value
    )

    if not city_name:
        return ""

    if "Addis Ababa" in city_name:
        return "Addis Ababa"

    return city_name


def clean_country_name(value):
    """
    Normalize Ethiopia's country name for
    internal full-address formatting.
    """

    country_name = _clean_text(
        value
    )

    if not country_name:
        return ""

    if country_name.casefold() in {
        "ethiopia",
        "ኢትዮጵያ",
    }:
        return "Ethiopia"

    return country_name


def build_display_name(
    primary_name,
    city_name,
):
    """
    Build a clean everyday Telegram display name.

    Addis Ababa is hidden because it is the
    current HABESHAGO MVP service city.

    A location outside Addis Ababa keeps
    its city name for clarity.
    """

    primary_name = _clean_text(
        primary_name
    )

    city_name = clean_city_name(
        city_name
    )

    if not primary_name:
        return city_name

    if not city_name:
        return primary_name

    if (
        city_name == "Addis Ababa"
        or primary_name.casefold()
        == city_name.casefold()
    ):
        return primary_name

    return f"{primary_name}, {city_name}"


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
    Convert coordinates into structured
    human-readable location information.

    Example:

        {
            "short": "Nefas Silk",
            "short_name": "Nefas Silk",
            "city": "Addis Ababa",
            "full": (
                "Nefas Silk, "
                "Addis Ababa, Ethiopia"
            ),
            "full_name": (
                "Nefas Silk, "
                "Addis Ababa, Ethiopia"
            ),
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

            address = (
                data.get("address")
                or {}
            )

            namedetails = (
                data.get("namedetails")
                or {}
            )

            top_level_name = _clean_text(
                data.get("name")
            )

            localized_name = _clean_text(
                namedetails.get(
                    f"name:{language}"
                )
                or namedetails.get("name")
            )

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
                    _clean_text(value)
                    for value in preferred_values
                    if is_meaningful_name(
                        value
                    )
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

            short_name = build_display_name(
                primary_name,
                city_name,
            )

            if not is_meaningful_name(
                short_name
            ):
                short_name = fallback

            full_parts = []

            for part in (
                primary_name,
                city_name,
                country_name,
            ):
                clean_part = _clean_text(
                    part
                )

                if not is_meaningful_name(
                    clean_part
                ):
                    continue

                if any(
                    clean_part.casefold()
                    == existing.casefold()
                    for existing
                    in full_parts
                ):
                    continue

                full_parts.append(
                    clean_part
                )

            full_name = ", ".join(
                full_parts
            )

            if not is_meaningful_name(
                full_name
            ):
                display_name = _clean_text(
                    data.get(
                        "display_name"
                    )
                )

                full_name = (
                    display_name
                    if is_meaningful_name(
                        display_name
                    )
                    else short_name
                )

            return {
                # Existing keys retained for
                # compatibility.
                "short": short_name,
                "full": full_name,

                # New structured metadata.
                "short_name": short_name,
                "city": city_name,
                "full_name": full_name,

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
        "short_name": fallback,
        "city": "",
        "full_name": fallback,
        "latitude": rounded_latitude,
        "longitude": rounded_longitude,
    }


def get_location_name(
    latitude,
    longitude,
    language="en",
):
    """
    Return only the short Telegram
    display name.
    """

    location = get_location_details(
        latitude,
        longitude,
        language,
    )

    return location["short_name"]