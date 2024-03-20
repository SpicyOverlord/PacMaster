import math

import pygame
from pygame import Surface

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.Map import DangerZone
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import isPortalPath, isInCenterArea
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class DebugHelper(object):
    """
    The DebugHelper offers static methods that can help with debugging agent behavior.
    """
    _instance = None

    shouldPause = False
    _enabled = True

    _screen = None
    _shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}

    GREEN = (0, 128, 0)
    LIGHTBLUE = (155, 226, 255)
    YELLOW = (255, 218, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 128, 255)
    PURPLE = (128, 0, 128)
    RED = (255, 30, 30)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DebugHelper, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def setScreen(screen: Surface):
        DebugHelper._screen = screen

    @staticmethod
    def pauseGame():
        """
            Pauses the game.
        """
        DebugHelper.shouldPause = True

    @staticmethod
    def disable():
        """
            Disables the DebugHelper.
        """
        DebugHelper._enabled = False

    @staticmethod
    def enable():
        """
            Enables the DebugHelper.
        """
        DebugHelper._enabled = True

    @staticmethod
    def drawLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5):
        """
            Draws a line between two vectors.
            :param startVector: The starting point of the line.
            :param endVector: The ending point of the line.
            :param color: The color of the line.
            :param width: The width of the line.
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.__addDrawObject__("line",
                                      [startVector.asInt(), endVector.asInt(), color, width])

    @staticmethod
    def drawDashedLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5,
                       dashLength: int = 10):
        """
            Draws a dashed line between two vectors.
            :param startVector: The starting point of the dashed line.
            :param endVector: The ending point of the dashed line.
            :param color: The color of the dashed line.
            :param width: The width of the dashed line.
            :param dashLength: The length of the dashes in the line.
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.__addDrawObject__("dashedLine",
                                      [startVector.asInt(), endVector.asInt(), color, width, dashLength])

    @staticmethod
    def drawDot(center: Vector2, radius: float, color: tuple[int, int, int]):
        """
            Draws a dot at a vector.
            :param center: The center of the dot.
            :param radius: The radius of the dot.
            :param color: The color of the dot.
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.__addDrawObject__("dot", [center.asInt(), radius, color])

    @staticmethod
    def drawDashedCircle(center: Vector2, radius: float, color: tuple[int, int, int], width=1, dashLength=10):
        """
            Draws a dashed circle around a vector.
            :param center: The center of the dashed circle.
            :param radius: The radius of the dashed circle.
            :param color: The color of the dashed circle.
            :param width: The width of the dashes.
            :param dashLength: The length of the dashes.
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.__addDrawObject__("dashedCircle",
                                      [center.asInt(), radius, color, width, dashLength])

    @staticmethod
    def drawPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5):
        """
        Draws a path between a list of vectors.
        :param path: The path to be drawn.
        :param color: The color of the drawn path.
        :param width: The width of the drawn path.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.drawDot(path[0], 3, DebugHelper.RED)
        DebugHelper.drawDot(path[-1], 3, DebugHelper.RED)
        for i in range(len(path) - 1):
            DebugHelper.drawLine(startVector=path[i], endVector=path[i + 1], color=color, width=width)

    @staticmethod
    def drawDashedPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5, dashLength: int = 10):
        """
        Draws a dashed path between a list of vectors.
        :param path: The path to be drawn.
        :param color: The color of the drawn path.
        :param width: The width of the drawn path.
        :param dashLength: The length of the dashes in the path.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        DebugHelper.drawDot(path[0], 3, DebugHelper.RED)
        DebugHelper.drawDot(path[-1], 3, DebugHelper.RED)
        for i in range(len(path) - 1):
            DebugHelper.drawDashedLine(startVector=path[i], endVector=path[i + 1], color=color,
                                       width=width, dashLength=dashLength)

    @staticmethod
    def drawGhostPaths(obs: Observation):
        """
        Draws the path of each ghost.
        :param obs: The current observation.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        for ghost in obs.getGhosts():
            DebugHelper.drawGhostPath(obs, ghost.name)

    @staticmethod
    def drawGhostPath(obs: Observation, ghostInt: int = BLINKY):
        """
        Draws the path of a specific ghost.
        :param obs: The current observation.
        :param ghostInt: The ghost to draw the path of.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        ghost = obs.getGhost(ghostInt)

        # ignore ghost if it is not dangerous
        if ghost.mode.current in [FREIGHT, SPAWN] or isInCenterArea(ghost.position):
            return

        # set line color and width based on ghost, to make it easier to tell which ghost path is which
        lineColor = (255, 255, 255)
        width = 5
        if ghostInt == BLINKY:
            lineColor = RED
            width = 7
        elif ghostInt == PINKY:
            lineColor = PINK
            width = 6
        elif ghostInt == INKY:
            lineColor = TEAL
            width = 5
        elif ghostInt == CLYDE:
            lineColor = ORANGE
            width = 4
        # calculate the ghost path
        path, _ = obs.map.calculateGhostPath(ghost=ghost, endVector=ghost.goal)

        # if the ghost can reach the goal, draw the path
        if len(path) != 0:
            DebugHelper.drawDashedPath(path, lineColor, width)

    @staticmethod
    def drawDangerZone(dangerZone: DangerZone):
        """
        Draws a danger zone.
        :param dangerZone: The danger zone to draw.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        # just to prevent errors.
        if dangerZone is None:
            return

        previousMapNode = None
        for mapNode in dangerZone.mapNodes:
            if previousMapNode is not None:
                DebugHelper.drawDashedLine(startVector=previousMapNode.position, endVector=mapNode.position,
                                           color=DebugHelper.YELLOW, width=3, dashLength=5)
            previousMapNode = mapNode

        for edgeMapNode in dangerZone.edgeMapNodes:
            DebugHelper.drawDot(edgeMapNode.position, 5, DebugHelper.GREEN)

    @staticmethod
    def drawMap(obs: Observation):
        """
        Draws the map/graph of the current level
        :param obs: The current Observation.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        for mapNode in obs.map.mapNodes:
            DebugHelper.drawDot(mapNode.position, 3, DebugHelper.BLUE)
            for neighbor in mapNode.neighborContainers:
                DebugHelper.drawLine(mapNode.position, neighbor.mapNode.position, DebugHelper.WHITE, 1)

    @staticmethod
    def drawDangerLevel(dangerLevel: float, vector: Vector2):
        """
        Draws a danger level at a vector.
        :param dangerLevel: The danger level.
        :param vector: The vector to draw the danger level at.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        # draw a dot with the size and color corresponding to how dangerous the position is.
        if 0.05 <= dangerLevel <= 1:
            DebugHelper.drawDot(vector, 5, DebugHelper.WHITE)
        elif dangerLevel < 2:
            DebugHelper.drawDot(vector, dangerLevel, DebugHelper.WHITE)
        elif dangerLevel > 30:
            DebugHelper.drawDot(vector, 10, DebugHelper.RED)
        else:
            if dangerLevel > 10:
                dangerLevel = 10
            DebugHelper.drawDot(vector, dangerLevel, DebugHelper.YELLOW)

    @staticmethod
    def drawDangerLevels(obs: Observation, dangerFunction: callable):
        """
        Draws the danger levels of each MapNode of the map.
        :param obs: The current Observation.
        :param dangerFunction: The function to calculate the danger level.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        for mapNode in obs.map.mapNodes:
            dangerLevel = dangerFunction(obs, mapNode.position)
            DebugHelper.drawDangerLevel(dangerLevel, mapNode.position)

    @staticmethod
    def __drawDashedLine__(startVector: Vector2, endVector: Vector2,
                           color: tuple[int, int, int], width=1, dash_length=5):
        x1, y1 = startVector
        x2, y2 = endVector
        dx, dy = x2 - x1, y2 - y1
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dash_count = int(distance / dash_length)

        for i in reversed(range(dash_count)):
            start = x1 + dx * (i / dash_count), y1 + dy * (i / dash_count)
            end = x1 + dx * ((i + 0.5) / dash_count), y1 + dy * ((i + 0.5) / dash_count)
            pygame.draw.line(DebugHelper._screen, color, start, end, width + ((i * 2) % 5 - 2))

    @staticmethod
    def __drawDashedCircle__(center: Vector2, radius: float, color: tuple[int, int, int], width=1, dash_length=5):
        total_circumference = 2 * math.pi * radius
        num_dashes = int(total_circumference / dash_length)
        angle_step = 2 * math.pi / num_dashes

        for dash in range(num_dashes):
            start_angle = dash * angle_step
            end_angle = start_angle + angle_step / 2  # Adjust this for dash thickness

            # Calculate bounding rectangle for the arc
            bounding_rect = (center[0] - radius, center[1] - radius, radius * 2, radius * 2)

            # Draw arc (part of the dashed circle)
            pygame.draw.arc(DebugHelper._screen, color, bounding_rect, start_angle, end_angle, width)

    @staticmethod
    def __addDrawObject__(drawObjectType: str, drawObject: list):
        """
        Adds a shape to the draw list.
        :param drawObjectType: The type of shape to draw.
        :param drawObject: The shape to draw.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        DebugHelper._shapesToDraw[drawObjectType].append(drawObject)

    @staticmethod
    def drawShapes():
        """
        Draws all shapes that have been added to the draw list.
        :return: None
        """
        if not DebugHelper._enabled:
            return

        for drawObjectType in DebugHelper._shapesToDraw.keys():
            for drawObject in DebugHelper._shapesToDraw[drawObjectType]:
                # skip portal paths
                if drawObjectType in ["line", "dashedLine"] and \
                        isPortalPath(Vector2(drawObject[0][0], drawObject[0][1]),
                                     Vector2(drawObject[1][0], drawObject[1][1])):
                    continue

                if drawObjectType == "line":
                    pygame.draw.line(surface=DebugHelper._screen,
                                     start_pos=drawObject[0], end_pos=drawObject[1],
                                     color=drawObject[2], width=drawObject[3])
                elif drawObjectType == "dashedLine":
                    DebugHelper.__drawDashedLine__(startVector=drawObject[0], endVector=drawObject[1],
                                                   color=drawObject[2], width=drawObject[3], dash_length=drawObject[4])
                elif drawObjectType == "dashedCircle":
                    DebugHelper.__drawDashedCircle__(center=drawObject[0], radius=drawObject[1], color=drawObject[2],
                                                     width=drawObject[3], dash_length=drawObject[4])
                elif drawObjectType == "dot":
                    pygame.draw.circle(surface=DebugHelper._screen, center=drawObject[0], radius=drawObject[1],
                                       color=drawObject[2])

        DebugHelper._shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}
