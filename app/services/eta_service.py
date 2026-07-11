import random


def calculate_eta(distance_km):
    """
    Calculate an estimated arrival time (ETA)
    based on ride distance.

    Returns ETA in minutes.
    """

    if distance_km <= 1:
        return random.randint(2, 4)

    if distance_km <= 3:
        return random.randint(4, 7)

    if distance_km <= 5:
        return random.randint(7, 10)

    if distance_km <= 10:
        return random.randint(10, 15)

    return random.randint(15, 25)