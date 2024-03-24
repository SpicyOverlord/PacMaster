import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class IslandCollectorAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawPelletLevels(obs)

        move = self.collect(obs)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT

        return move

    def collect(self, obs: Observation):
        pacmanPosition = obs.getPacmanPosition()

        nextPos = self.calculateNearestIslandPosition(obs)
        nextPosMapPosition = obs.map.createMapPosition(nextPos)
        DebugHelper.drawDot(nextPos, 3, DebugHelper.RED)

        paths = [
            obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode1.position),
            obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode2.position)
            if nextPosMapPosition.isBetweenMapNodes else (None, float('inf'))
        ]

        # Prefer path that includes nextPos and has the shortest distance
        preferred_path, preferred_distance = None, float('inf')

        for path, distance in paths:
            if path and obs.isVectorInPath(path, nextPos) and (preferred_path is None or distance < preferred_distance):
                preferred_path, preferred_distance = path, distance

        # If no path includes nextPos or if both paths have been calculated and neither includes nextPos,
        # choose the shorter path
        if preferred_path is None:
            preferred_path, preferred_distance = min(paths, key=lambda x: x[1])

        # Draw the preferred path and return direction of the second point
        if preferred_path and len(preferred_path) > 1:
            DebugHelper.drawPath(preferred_path, DebugHelper.YELLOW, 10)
            return self.getDirection(obs, preferred_path[1])
        else:
            # If there is no path or the path doesn't have a second point, move towards nextPos directly
            return self.getDirection(obs, nextPos)

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
                    if (abs(currentPosition.x - pelletPosition2.x) < 30 and
                            abs(currentPosition.y - pelletPosition2.y) < 30):
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
            DebugHelper.drawDot(position, 5, DebugHelper.WHITE)
            pass
        # draw islands
        for i, island in enumerate(islands):
            for position in island:
                DebugHelper.drawDot(position, 4, colors[i % 6])
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
