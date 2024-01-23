from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


def roundVector(vector2: Vector2) -> Vector2:
    return Vector2(round(vector2.x), round(vector2.y))


def manhattenDistance(a: Vector2, b: Vector2) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def getOppositeDirection(direction: int) -> int:
    if direction == UP:
        return DOWN
    elif direction == DOWN:
        return UP
    elif direction == LEFT:
        return RIGHT
    elif direction == RIGHT:
        return LEFT


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
