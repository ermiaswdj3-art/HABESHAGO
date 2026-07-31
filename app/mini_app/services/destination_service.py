"""
Destination Service

Provides destination suggestions for the HABESHAGO Mini App.

Currently uses demonstration data.
Future versions will connect to:
- Search API
- Saved places
- Recent destinations
- Public transport stops
- Landmarks
"""

DESTINATIONS = [
    {
        "icon": "📍",
        "name": "Bole International Airport",
        "description": "Airport Road, Addis Ababa",
    },
    {
        "icon": "🏙️",
        "name": "Meskel Square",
        "description": "Kirkos, Addis Ababa",
    },
    {
        "icon": "🏘️",
        "name": "Ayat",
        "description": "East Addis Ababa",
    },
    {
        "icon": "🛍️",
        "name": "Megenagna",
        "description": "Yeka, Addis Ababa",
    },
    {
        "icon": "🏢",
        "name": "Kazanchis",
        "description": "Central Addis Ababa",
    },
]


def get_destination_suggestions():
    """
    Return all available destination suggestions.

    Future versions may:
    - Sort by popularity
    - Personalize results
    - Query a database
    - Call a search API
    """
    return DESTINATIONS


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_destination_suggestions())