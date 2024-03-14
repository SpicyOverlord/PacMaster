from datetime import datetime

from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


def roundVector(vector: Vector2) -> Vector2:
    return Vector2(round(vector.x), round(vector.y))


def manhattanDistance(a: Vector2, b: Vector2) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def distanceSquared(a: Vector2, b: Vector2) -> int:
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

def getCurrentTimestamp() -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp_str

def getOppositeDirection(direction: int) -> int:
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
    if direction == UP:
        return "UP"
    if direction == DOWN:
        return "DOWN"
    if direction == LEFT:
        return "LEFT"
    if direction == RIGHT:
        return "RIGHT"

    raise Exception(f"Direction '{direction}' not recognized")


def isPortalPath(startVector: Vector2, endVector: Vector2) -> bool:
    # real distance is TILESIZE * 26, but we use 24 to be safe
    portalDistance = WINDOWSIZE * 24
    return abs(startVector.x - endVector.x) > portalDistance and startVector.y == endVector.y


def isInCenterArea(vector: Vector2):
    return 200 <= vector.x < 350 and 281 <= vector.y < 390


def distanceToNearestEdge(vector: Vector2) -> int:
    distance_from_left = vector.x - 20
    distance_from_right = 520 - vector.x
    distance_from_top = vector.y - 80
    distance_from_bottom = 640 - vector.y

    return min(distance_from_left, distance_from_right, distance_from_top, distance_from_bottom)


def secondsToTime(seconds) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:03}h {minutes:02}m {seconds:02}s"
