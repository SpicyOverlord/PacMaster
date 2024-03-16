import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class CollectorAgent2(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

        self.pelletTarget = None

    def calculateNextMove(self, obs: Observation):

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawPelletLevels(obs)

        nextPos = self.calculateNearestIslandPosition(obs)
        DebugHelper.drawDot(nextPos, 3, DebugHelper.RED)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT

        pacmanPosition = obs.getPacmanPosition()
        # mapPos = obs.map.createMapPosition(pacmanPosition)
        # if mapPos.isBetweenMapNodes:
        #     return STOP

        if self.pelletTarget is None:
            nextPosMapPosition = obs.map.createMapPosition(nextPos)
            path, distance = obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode1.position)

            path2 = []
            distance2 = 0
            DebugHelper.drawDot(nextPosMapPosition.mapNode1.position, 4, DebugHelper.GREEN)
            if nextPosMapPosition.isBetweenMapNodes:
                path2, distance2 = obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode2.position)
                if distance2 > distance:
                    path = path2
                    # distance = distance2

                DebugHelper.drawDot(nextPosMapPosition.mapNode2.position, 4, DebugHelper.GREEN)
                DebugHelper.drawLine(nextPosMapPosition.mapNode1.position, nextPosMapPosition.mapNode2.position, DebugHelper.GREEN, 2)

            if len(path) < 3:
                self.pelletTarget = nextPos
                return self.getDirection(obs, nextPos)

            DebugHelper.drawDashedPath(path, DebugHelper.YELLOW, 3, 10)
            # DebugHelper.pauseGame()
            self.pelletTarget = path[1]
            return self.getDirection(obs, path[1])

        DebugHelper.drawDashedCircle(self.pelletTarget, 10, DebugHelper.LIGHTBLUE, 5, 20)
        if manhattanDistance(pacmanPosition, self.pelletTarget) < 10:
            self.pelletTarget = None
            return STOP
        return self.getDirection(obs, self.pelletTarget)

    def calculateNearestIslandPosition(self, obs: Observation):
        pelletPositions = obs.getPelletPositions()

        colors = [DebugHelper.GREEN, DebugHelper.RED, DebugHelper.BLUE, DebugHelper.YELLOW,
                  DebugHelper.PURPLE, DebugHelper.LIGHTBLUE]

        visited = set()
        islands = []
        for pelletPosition in pelletPositions:
            if pelletPosition.asTuple() in visited:
                continue

            island = []
            queue = [pelletPosition.asTuple()]
            while queue:
                current = queue.pop(0)

                if current in visited:
                    continue

                currentPosition = Vector2(current[0], current[1])

                visited.add(current)
                island.append(currentPosition)

                for pelletPosition2 in pelletPositions:
                    if (abs(currentPosition.x - pelletPosition2.x) < 60 and
                            abs(currentPosition.y - pelletPosition2.y) < 60):
                        pelletTuple2 = pelletPosition2.asTuple()
                        if pelletTuple2 in visited:
                            continue
                        queue.append(pelletTuple2)

            islands.append(island)

        # calculate the distance to each island
        pacmanPosition = obs.getPacmanPosition()
        islandDistances = []
        closestIslandPositions = []
        for i, island in enumerate(islands):
            minDistance = 999999
            minPosition = None
            for position in island:
                distance = manhattanDistance(pacmanPosition, position)
                if distance < minDistance:
                    minDistance = distance
                    minPosition = position

            islandDistances.append(minDistance)
            closestIslandPositions.append(minPosition)

        # find island with the highest value
        highestIslandValue = 0
        highestIslandIndex = 0
        for i, island in enumerate(islands):
            islandValue = (10 / len(island)) * (100 / (islandDistances[i] + 1))

            if islandValue > highestIslandValue:
                highestIslandValue = islandValue
                highestIslandIndex = i

        # draw the highest island
        for position in islands[highestIslandIndex]:
            # DebugHelper.drawDot(position, 10, DebugHelper.WHITE)
            pass
        # draw islands
        for i, island in enumerate(islands):
            for position in island:
                # DebugHelper.drawDot(position, 5, colors[i % 6])
                pass

        return closestIslandPositions[highestIslandIndex]

    def getDirection(self, obs: Observation, target: Vector2) -> int:
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == target.y:
            if pacmanPosition.x < target.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < target.y:
                return DOWN
            else:
                return UP
