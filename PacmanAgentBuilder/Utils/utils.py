from __future__ import annotations

import base64
import csv
import os
import random
from datetime import datetime
from typing import List

from PacmanAgentBuilder.Utils.Snapshot import Snapshot
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2

global_row_count = 0


def roundVector(vector: Vector2) -> Vector2:
    """
    Rounds the x and y values of the vector to the nearest integer
    :param vector: The vector to round
    :return: A new vector with the rounded values
    """
    return Vector2(round(vector.x), round(vector.y))


def manhattanDistance(a: Vector2, b: Vector2) -> int:
    """
    Calculates the manhattan distance between two vectors
    :param a: The first vector
    :param b: The second vector
    :return: The manhattan distance between the two vectors
    """
    return abs(a.x - b.x) + abs(a.y - b.y)


def squaredDistance(a: Vector2, b: Vector2) -> int:
    """
    Calculates the squared distance between two vectors
    :param a: The first vector
    :param b: The second vector
    :return: The squared distance between the two vectors
    """
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def getCurrentTimestamp() -> str:
    """
    Gets the current timestamp in the format "YYYY-MM-DD HH:MM:SS"
    :return: The current timestamp
    """
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp_str


def getOppositeDirection(direction: int) -> int:
    """
    Gets the opposite direction of the given direction
    :param direction: The direction
    :return: The opposite direction
    """
    return direction * -1
    # if direction == UP:
    #     return DOWN
    # elif direction == DOWN:
    #     return UP
    # elif direction == LEFT:
    #     return RIGHT
    # elif direction == RIGHT:
    #     return LEFT


def directionToString(direction: int):
    """
    :param direction: The direction
    :return: The string representation of the direction
    """
    if direction == UP:
        return "UP"
    if direction == DOWN:
        return "DOWN"
    if direction == LEFT:
        return "LEFT"
    if direction == RIGHT:
        return "RIGHT"
    if direction == STOP:
        return "STOP"

    raise Exception(f"Direction '{direction}' not recognized")


def isPortalPath(startVector: Vector2, endVector: Vector2) -> bool:
    """
    Checks if the path between two vectors is a portal path
    :param startVector: The first vector
    :param endVector: The second vector
    :return: True if the path is a portal path, False otherwise
    """
    portalDistance = WINDOWSIZE * 24
    return abs(startVector.x - endVector.x) > portalDistance and startVector.y == endVector.y


def isInCenterArea(vector: Vector2):
    """
    Checks if the given vector is in the center area (the ghosts' starting area)
    :param vector: The vector to check
    :return: True if the vector is in the center area, False otherwise
    """
    return 200 <= vector.x < 350 and 281 <= vector.y < 390


def distanceToNearestEdge(vector: Vector2) -> int:
    """
    Calculates the distance from the given vector to the nearest edge of the map
    :param vector: The vector
    :return: The distance to the nearest edge
    """
    distance_from_left = vector.x - 20
    distance_from_right = 520 - vector.x
    distance_from_top = vector.y - 80
    distance_from_bottom = 640 - vector.y

    return min(distance_from_left, distance_from_right, distance_from_top, distance_from_bottom)


def secondsToTime(seconds) -> str:
    """
    Converts seconds to a time string in the format "HHh MMm SSs"
    :param seconds: The seconds
    :return: The time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:03}h {minutes:02}m {seconds:02}s"


def directionToIndex(direction: int) -> int:
    if direction == UP:
        return 0
    if direction == DOWN:
        return 1
    if direction == LEFT:
        return 2
    if direction == RIGHT:
        return 3
    return -1


def indexToDirection(index: int) -> int:
    if index == 0:
        return UP
    if index == 1:
        return DOWN
    if index == 2:
        return LEFT
    if index == 3:
        return RIGHT
    return STOP


def directionToVector(direction: int) -> Vector2:
    """
    Converts a direction to a vector
    :param direction: The direction
    :return: The vector
    """
    if direction == UP:
        return Vector2(0, -1)
    if direction == DOWN:
        return Vector2(0, 1)
    if direction == LEFT:
        return Vector2(-1, 0)
    if direction == RIGHT:
        return Vector2(1, 0)
    if direction == STOP:
        return Vector2(0, 0)

    raise Exception(f"Direction '{direction}' not recognized")


# def getHash(lst: List[int]) -> int:
#
#     h = 97
#     for j in range(len(lst)):
#         value = lst[j]
#         if value in [UP, DOWN, LEFT, RIGHT]:
#             value = directionToIndex(value)
#         h = h * 7 + value
#
#     # base 64
#     # num_bytes = h.to_bytes((h.bit_length() + 7) // 8, 'big')
#     # base64_str = base64.b64encode(num_bytes)
#     #
#     # hashStr = base64_str.decode()
#
#     # hashStr = h
#     # if lst[1] == 5 and lst[2] == 13:
#     #     print("UP", hashStr, hash(hashStr))
#     # if lst[1] == 12 and lst[2] == 22:
#     #     print("LEFT", hashStr, hash(hashStr))
#
#     return h

# def getHash(lst: List[int]) -> int:
#     h = 97
#     max_int = 2**31 - 1  # Maximum integer size for a 32-bit integer
#     for j in range(len(lst)):
#         value = lst[j]
#         if value in [UP, DOWN, LEFT, RIGHT]:
#             value = directionToIndex(value)
#         h = (h * 7 + value) % max_int  # Use modulo operation to ensure h is less than max_int
#     return h

def getHash(lst: List[int]) -> int:
    # Fowler–Noll–Vo (FNV) hash function
    FNV_prime = 0x811C9DC5
    FNV_offset_basis = 0x01000193

    h = FNV_offset_basis
    for value in lst:
        if value in [UP, DOWN, LEFT, RIGHT]:
            value = directionToIndex(value)
        h = (h * FNV_prime) ^ value
        h = h & 0xFFFFFFFF  # Ensure h is within 32-bit range

    return h
