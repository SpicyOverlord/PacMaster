from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


def roundVector(vector: Vector2) -> Vector2:
    return Vector2(round(vector.x), round(vector.y))


def clampVectorToNonNegative(vector: Vector2):
    return Vector2(max(0, vector.x), max(0, vector.y))


def manhattanDistance(a: Vector2, b: Vector2) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def distanceSquared(a: Vector2, b: Vector2) -> int:
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


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
    # real distance is TILESIZE * 26, but we want to be safe
    portalDistance = TILESIZE * 24
    return abs(startVector.x - endVector.x) > portalDistance and startVector.y == endVector.y


def distanceToNearestEdge(vector: Vector2) -> int:
    distance_from_left = vector.x - 20
    distance_from_right = 520 - vector.x
    distance_from_top = vector.y - 80
    distance_from_bottom = 640 - vector.y

    return min(distance_from_left, distance_from_right, distance_from_top, distance_from_bottom)
