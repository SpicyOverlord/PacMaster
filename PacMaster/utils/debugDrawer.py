import math

import pygame
from pygame import Surface

from Pacman_Complete.vector import Vector2


class DebugDrawer(object):
    _instance = None
    _screen = None
    _shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}
    GREEN = (0, 128, 0)
    BLUE = (135, 206, 235)
    YELLOW = (255, 218, 0)
    WHITE = (255, 255, 255)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DebugDrawer, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def setScreen(screen: Surface):
        DebugDrawer._screen = screen

    @staticmethod
    def drawLine(vector1: Vector2, vector2: Vector2, color: tuple[int, int, int], width: int = 5):
        DebugDrawer.__addDrawObject__("line",
                                      [vector1.asInt(), vector2.asInt(), color, width])

    @staticmethod
    def drawPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5):
        for i in range(len(path) - 1):
            DebugDrawer.__addDrawObject__("line",
                                          [path[i].asInt(), path[i + 1].asInt(), color, width])

    @staticmethod
    def drawDashedPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5, dashLength: int = 10):
        for i in range(len(path) - 1):
            DebugDrawer.__addDrawObject__("dashedLine",
                                          [path[i].asInt(), path[i + 1].asInt(), color, width, dashLength])

    @staticmethod
    def drawDashedLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5,
                       dashLength: int = 10):
        DebugDrawer.__addDrawObject__("dashedLine",
                                      [startVector, endVector, color, width, dashLength])

    @staticmethod
    def drawDashedCircle(center: Vector2, radius: float, color: tuple[int, int, int], width=1, dash_length=10):
        DebugDrawer.__addDrawObject__("dashedCircle",
                                      [center, radius, color, width, dash_length])

    @staticmethod
    def drawDot(position: Vector2, color: tuple[int, int, int], radius: float = 3.0):
        DebugDrawer.__addDrawObject__("dot", [position.asInt(), color, radius])

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
            pygame.draw.line(DebugDrawer._screen, color, start, end, width + ((i * 2) % 5 - 2))

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
            pygame.draw.arc(DebugDrawer._screen, color, bounding_rect, start_angle, end_angle, width)

    @staticmethod
    def __addDrawObject__(drawObjectType: str, drawObject: list):
        DebugDrawer._shapesToDraw[drawObjectType].append(drawObject)

    @staticmethod
    def drawShapes():
        for drawObjectType in DebugDrawer._shapesToDraw.keys():
            for drawObject in DebugDrawer._shapesToDraw[drawObjectType]:
                # skip portal path
                if (drawObjectType in ["line", "dashedLine"] and
                        DebugDrawer.isPortalPath(startTuple=drawObject[0], endTuple=drawObject[1])):
                    continue

                if drawObjectType == "line":
                    pygame.draw.line(surface=DebugDrawer._screen,
                                     start_pos=drawObject[0], end_pos=drawObject[1],
                                     color=drawObject[2], width=drawObject[3])
                elif drawObjectType == "dashedLine":
                    DebugDrawer.__drawDashedLine__(startVector=drawObject[0], endVector=drawObject[1],
                                                   color=drawObject[2], width=drawObject[3], dash_length=drawObject[4])
                elif drawObjectType == "dashedCircle":
                    DebugDrawer.__drawDashedCircle__(center=drawObject[0], radius=drawObject[1], color=drawObject[2],
                                                     width=drawObject[3], dash_length=drawObject[4])
                elif drawObjectType == "dot":
                    pygame.draw.circle(surface=DebugDrawer._screen, center=drawObject[0],
                                       color=drawObject[1], radius=drawObject[2])

        DebugDrawer._shapesToDraw = {"line": [], "dashedLine": [], "dashedCircle": [], "dot": []}

    @staticmethod
    def isPortalPath(startTuple: tuple[int, int], endTuple: tuple[int, int]) -> bool:
        startX, startY = startTuple
        endX, endY = endTuple
        return startX == 272 and startY == 272 and min(startY, endY) == 0 and max(startY, endY) == 432
