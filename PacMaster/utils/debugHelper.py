import math

import pygame
from pygame import Surface

from PacMaster.utils.map import DangerZone, Map
from PacMaster.utils.utils import isPortalPath
from Pacman_Complete.constants import TILESIZE
from Pacman_Complete.vector import Vector2


class DebugHelper(object):
    _instance = None

    shouldPause = False

    _screen = None
    _shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}

    GREEN = (0, 128, 0)
    LIGHTBLUE = (155, 226, 255)
    YELLOW = (255, 218, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 128, 255)
    PURPLE = (128, 0, 128)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DebugHelper, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def setScreen(screen: Surface):
        DebugHelper._screen = screen

    @staticmethod
    def pauseGame():
        DebugHelper.shouldPause = True

    @staticmethod
    def drawLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5):
        DebugHelper.__addDrawObject__("line",
                                      [startVector.asInt(), endVector.asInt(), color, width])

    @staticmethod
    def drawDashedLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5,
                       dashLength: int = 10):
        DebugHelper.__addDrawObject__("dashedLine",
                                      [startVector.asInt(), endVector.asInt(), color, width, dashLength])

    @staticmethod
    def drawDashedCircle(center: Vector2, radius: float, color: tuple[int, int, int], width=1, dash_length=10):
        DebugHelper.__addDrawObject__("dashedCircle",
                                      [center.asInt(), radius, color, width, dash_length])

    @staticmethod
    def drawDot(position: Vector2, color: tuple[int, int, int], radius: float = 3.0):
        DebugHelper.__addDrawObject__("dot",
                                      [position.asInt(), color, radius])

    @staticmethod
    def drawMap(map: Map):
        for mapNode in map.mapNodes:
            DebugHelper.drawDot(mapNode.position, DebugHelper.LIGHTBLUE, 5)
            for neighbor in mapNode.neighborContainers:
                DebugHelper.drawLine(mapNode.position, neighbor.mapNode.position, DebugHelper.BLUE, 2)

    @staticmethod
    def drawPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5):
        for i in range(len(path) - 1):
            DebugHelper.drawLine(startVector=path[i], endVector=path[i + 1], color=color, width=width)

    @staticmethod
    def drawDashedPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5, dashLength: int = 10):
        for i in range(len(path) - 1):
            DebugHelper.drawDashedLine(startVector=path[i], endVector=path[i + 1], color=color,
                                       width=width, dashLength=dashLength)

    @staticmethod
    def drawDangerZone(dangerZone: DangerZone):
        previousMapNode = None
        for mapNode in dangerZone.mapNodes:
            if previousMapNode is not None:
                DebugHelper.drawDashedLine(startVector=previousMapNode.position, endVector=mapNode.position,
                                           color=DebugHelper.YELLOW, width=3, dashLength=5)
            previousMapNode = mapNode

        for edgeMapNode in dangerZone.edgeMapNodes:
            DebugHelper.drawDot(edgeMapNode.position, DebugHelper.GREEN, 5)

    @staticmethod
    def __drawDashedLine__(startVector: Vector2, endVector: Vector2,
                           color: tuple[int, int, int], width=1, dash_length=5):
        x1, y1 = startVector
        x2, y2 = endVector
        dx, dy = x2 - x1, y2 - y1
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dash_count = int(distance / dash_length)

        for i in range(dash_count):
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
            bounding_rect = (center.x - radius, center.y - radius, radius * 2, radius * 2)

            # Draw arc (part of the dashed circle)
            pygame.draw.arc(DebugHelper._screen, color, bounding_rect, start_angle, end_angle, width)

    @staticmethod
    def __addDrawObject__(drawObjectType: str, drawObject: list):
        DebugHelper._shapesToDraw[drawObjectType].append(drawObject)

    @staticmethod
    def drawShapes():
        for drawObjectType in DebugHelper._shapesToDraw.keys():
            for drawObject in DebugHelper._shapesToDraw[drawObjectType]:
                # skip portal path
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
                    pygame.draw.circle(surface=DebugHelper._screen, center=drawObject[0],
                                       color=drawObject[1], radius=drawObject[2])

        DebugHelper._shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}
