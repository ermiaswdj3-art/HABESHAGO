import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the straight-line distance between two GPS coordinates.
    Returns the distance in kilometers.
    """

    latitude_difference = lat2 - lat1
    longitude_difference = lon2 - lon1

    distance = math.sqrt(
        latitude_difference ** 2 +
        longitude_difference ** 2
    )

    return distance * 111