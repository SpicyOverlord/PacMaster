import math

import pygame
from pygame import Surface

from Pacman_Complete.vector import Vector2


class DebugDrawer(object):
    _instance = None
    _screen = None
    _shapesToDraw = []
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
        DebugDrawer._shapesToDraw.append(["line", vector1.asTuple(), vector2.asTuple(), color, width])

    @staticmethod
    def drawPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5):
        for i in range(len(path) - 1):
            DebugDrawer.drawLine(path[i], path[i + 1], color, width)

    @staticmethod
    def drawDashedPath(path: list[Vector2], color: tuple[int, int, int], width: int = 5, dashLength: int = 10):
        for i in range(len(path) - 1):
            DebugDrawer.drawDashedLine(path[i], path[i + 1], color, width, dashLength)

    @staticmethod
    def drawDashedLine(startVector: Vector2, endVector: Vector2, color: tuple[int, int, int], width: int = 5,
                       dashLength: int = 10):
        DebugDrawer._shapesToDraw.append(
            ["dashedLine", startVector.asTuple(), endVector.asTuple(), color, width, dashLength])

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
            pygame.draw.line(DebugDrawer._screen, color, start, end, width + (i % 3 - 1))

    @staticmethod
    def drawShapes():
        for shape in DebugDrawer._shapesToDraw:
            if shape[0] == "line":
                pygame.draw.line(surface=DebugDrawer._screen,
                                 start_pos=shape[1], end_pos=shape[2],
                                 color=shape[3], width=shape[4])
            elif shape[0] == "dashedLine":
                DebugDrawer.__drawDashedLine__(startVector=shape[1], endVector=shape[2],
                                               color=shape[3], width=shape[4], dash_length=shape[5])

        DebugDrawer._shapesToDraw = []
