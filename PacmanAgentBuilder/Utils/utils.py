from __future__ import annotations

import csv
import os
import random
import time
from datetime import datetime
from typing import List

from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


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


global_row_count = 0
global_last_time = time.time()


def save_snapshots_to_file(snapshots, fileName):
    directory = 'Data'
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f'{directory}/{fileName}.csv'
    header = ['current_level_layout',
              'pacman_x', 'pacman_y',
              'ghost1_x', 'ghost1_y',
              'ghost2_x', 'ghost2_y',
              'ghost3_x', 'ghost3_y',
              'ghost4_x', 'ghost4_y',
              'ghost1_direction_x', 'ghost1_direction_y',
              'ghost2_direction_x', 'ghost2_direction_y',
              'ghost3_direction_x', 'ghost3_direction_y',
              'ghost4_direction_x', 'ghost4_direction_y',
              'ghost1_active', 'ghost2_active', 'ghost3_active', 'ghost4_active',
              'nearest_pellet1_x', 'nearest_pellet1_y',
              'nearest_pellet2_x', 'nearest_pellet2_y',
              'nearest_pellet3_x', 'nearest_pellet3_y',
              'nearest_pellet4_x', 'nearest_pellet4_y',
              'nearest_pellet5_x', 'nearest_pellet5_y',
              'game_ended',
              'legal_move_up', 'legal_move_down', 'legal_move_left', 'legal_move_right',
              'made_move_up', 'made_move_down', 'made_move_left', 'made_move_right']

    snapshots[-1].setGameEnded()
    lastSnapshot = snapshots[-1]

    snapshots = [snapshot for snapshot in snapshots if random.random() < 0.20]  # keep ~20% of the snapshots

    if snapshots[-1] != lastSnapshot:
        snapshots.append(lastSnapshot)

    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        global global_row_count
        global_row_count += len(snapshots)

        global global_last_time
        print(
            f" - game snapshots: {len(snapshots)} -  Total Snapshots: {global_row_count} - Time: {secondsToTime(time.time() - global_last_time)}")

        if os.stat(filename).st_size == 0:  # check if file is empty
            writer.writerow(header)  # write header

        for snapshot in snapshots:
            if snapshot is None:
                continue

            try:
                snapshotArray = snapshot.getArray()
                writer.writerow(snapshotArray)
            except Exception as e:
                pass
