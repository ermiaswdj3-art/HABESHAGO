import logging
import time
from functools import lru_cache

import requests

from app.services.popular_places import (
    POPULAR_SEARCH_ALIASES,
)


logger = logging.getLogger(__name__)

NOMINATIM_SEARCH_URL = (
    "https://nominatim.openstreetmap.org/search"
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


def _clean_city_name(value):
    """
    Normalize multilingual Addis Ababa labels.
    """

    city_name = _clean_text(value)

    if not city_name:
        return ""

    if "Addis Ababa" in city_name:
        return "Addis Ababa"

    return city_name


def _get_city_name(result):
    """
    Extract the most useful city or administrative
    area from a Nominatim search result.
    """

    address = result.get("address") or {}

    return _clean_city_name(
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("state_district")
        or address.get("state")
    )


def _build_display_name(
    primary_name,
    city_name,
):
    """
    Build a clean Telegram display name.

    Addis Ababa is hidden because it is the
    current HABESHAGO MVP service city.

    Locations outside Addis Ababa keep their
    city name for clarity.
    """

    primary_name = _clean_text(
        primary_name
    )

    city_name = _clean_city_name(
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


def _build_primary_name(result):
    """
    Extract the most recognizable landmark,
    neighbourhood, building or road name.
    """

    address = result.get("address") or {}

    return (
        _clean_text(result.get("name"))
        or _clean_text(address.get("amenity"))
        or _clean_text(address.get("tourism"))
        or _clean_text(address.get("shop"))
        or _clean_text(address.get("office"))
        or _clean_text(address.get("aeroway"))
        or _clean_text(address.get("railway"))
        or _clean_text(address.get("building"))
        or _clean_text(address.get("residential"))
        or _clean_text(address.get("locality"))
        or _clean_text(address.get("hamlet"))
        or _clean_text(address.get("city_block"))
        or _clean_text(address.get("neighbourhood"))
        or _clean_text(address.get("quarter"))
        or _clean_text(address.get("suburb"))
        or _clean_text(address.get("borough"))
        or _clean_text(address.get("city_district"))
        or _clean_text(address.get("county"))
        or _clean_text(address.get("road"))
    )


def _build_short_name(result):
    """
    Create a concise destination name for
    Telegram buttons and ride summaries.
    """

    primary_name = _build_primary_name(
        result
    )

    city_name = _get_city_name(
        result
    )

    display_name = _build_display_name(
        primary_name,
        city_name,
    )

    if display_name:
        return display_name

    fallback = _clean_text(
        result.get("display_name")
    )

    if fallback:
        return fallback.split(",")[0].strip()

    return "Unknown destination"


def _normalize_destination_name(name):
    """
    Normalize names for duplicate detection.

    Examples:
        "Bole" -> "bole"
        "Bole, Addis Ababa" -> "bole"
    """

    normalized = _clean_text(
        name
    ).casefold()

    if normalized.endswith(
        ", addis ababa"
    ):
        normalized = normalized.removesuffix(
            ", addis ababa"
        ).strip()

    return normalized


def _get_search_queries(query):
    """
    Return smarter search phrases for common
    Addis Ababa destination names.
    """

    clean_query = _clean_text(
        query
    )

    normalized_query = (
        clean_query.casefold()
    )

    aliases = POPULAR_SEARCH_ALIASES.get(
        normalized_query
    )

    if aliases:
        return aliases

    return [
        f"{clean_query} Addis Ababa",
        clean_query,
    ]


@lru_cache(maxsize=1000)
def _search_cached(
    query,
    language,
):
    """
    Search Nominatim and cache identical queries.

    More than five raw results are requested because
    filtering and duplicate removal may discard some.
    """

    response = requests.get(
        NOMINATIM_SEARCH_URL,
        params={
            "q": query,
            "format": "jsonv2",
            "addressdetails": 1,
            "namedetails": 1,
            "limit": 20,
            "countrycodes": "et",
            "accept-language": language,
        },
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def search_destinations(
    query,
    language="en",
):
    """
    Search for up to five destinations in Addis Ababa.

    Results are:
    - restricted to Ethiopia;
    - filtered to Addis Ababa when city data exists;
    - deduplicated by name and coordinates;
    - formatted without repeating Addis Ababa
      in everyday Telegram display names.

    Returns:
        [
            {
                "name": "Bole Medhanialem",
                "short_name": "Bole Medhanialem",
                "city": "Addis Ababa",
                "full_name": "...",
                "latitude": 8.98,
                "longitude": 38.79,
            }
        ]
    """

    clean_query = _clean_text(
        query
    )

    if len(clean_query) < 2:
        return []

    last_error = None

    for attempt in range(2):
        try:
            search_queries = (
                _get_search_queries(
                    clean_query
                )
            )

            raw_results = []

            for search_query in search_queries:
                query_results = (
                    _search_cached(
                        search_query.casefold(),
                        language,
                    )
                )

                raw_results.extend(
                    query_results
                )

            destinations = []
            seen_names = set()
            seen_coordinates = set()

            for result in raw_results:
                try:
                    latitude = float(
                        result["lat"]
                    )

                    longitude = float(
                        result["lon"]
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    continue

                city_name = _get_city_name(
                    result
                )

                # HABESHAGO's MVP currently operates
                # inside Addis Ababa.
                #
                # Exclude results whose city is clearly
                # another Ethiopian city or region.
                if (
                    city_name
                    and city_name
                    != "Addis Ababa"
                ):
                    continue

                primary_name = (
                    _build_primary_name(
                        result
                    )
                )

                short_name = (
                    _build_display_name(
                        primary_name,
                        city_name,
                    )
                )

                if not short_name:
                    short_name = (
                        _build_short_name(
                            result
                        )
                    )

                normalized_name = (
                    _normalize_destination_name(
                        short_name
                    )
                )

                if (
                    not normalized_name
                    or normalized_name
                    == "unknown destination"
                ):
                    continue

                if normalized_name in seen_names:
                    continue

                coordinate_key = (
                    round(latitude, 5),
                    round(longitude, 5),
                )

                if (
                    coordinate_key
                    in seen_coordinates
                ):
                    continue

                seen_names.add(
                    normalized_name
                )

                seen_coordinates.add(
                    coordinate_key
                )

                full_name = _clean_text(
                    result.get(
                        "display_name"
                    )
                )

                destinations.append(
                    {
                        # Retained for compatibility with
                        # the existing destination handler.
                        "name": short_name,

                        "short_name": short_name,
                        "city": city_name,
                        "full_name": full_name,
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                )

                if len(destinations) == 5:
                    break

            return destinations

        except requests.RequestException as error:
            last_error = error

            logger.warning(
                (
                    "Destination search attempt %s "
                    "failed for '%s': %s"
                ),
                attempt + 1,
                clean_query,
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
                    "Invalid destination search "
                    "response for '%s': %s"
                ),
                clean_query,
                error,
            )

            break

    logger.warning(
        "Destination search failed for '%s': %s",
        clean_query,
        last_error,
    )

    return []