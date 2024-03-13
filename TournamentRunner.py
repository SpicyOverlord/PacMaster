import random
import sys
import time
from datetime import datetime
import multiprocessing
import os

import numpy as np

from PacmanAgentBuilder.Utils.GameStats import GameStats

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Agents.FirstRealAgent import FirstRealAgent
from PacmanAgentBuilder.Agents.HumanAgent import HumanAgent
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import calculatePerformanceOverXGames
from PacmanAgentBuilder.Utils.utils import secondsToTime, getCurrentTimestamp


class TournamentRunner:
    @staticmethod
    def startNewTournament(agentClass: type[IAgent], populationSize: int, generationCount: int, mutationRate: float,
                           gameCount: int, cpuCount):
        tournamentStartTime = time.time()

        logFileName = f"Tournaments/{agentClass.__name__}_{getCurrentTimestamp()}.txt"

        allMembers = []

        totalGameCount = populationSize * generationCount * gameCount

        bestOfEachGenerations = []

        poolSize = max(int(populationSize * 0.2), 2)
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / (generationCount - 5))) * (1 / mutationRate) ** (
                1 / (generationCount - 5))

        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        BestWeightContainer = agentClass.getBestWeightContainer()

        weightList = [
            WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 16.024,
                             'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 2069.434, 'wayTooCloseValue': 3089.918,
                             'tooCloseValue': 1456.791, 'dangerZoneMultiplier': 0.005,
                             'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431,
                             'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.208,
                             'edgeMultiplier': 3.232}),
            WeightContainer({'fleeThreshold': 0.168, 'pelletLevelDistance': 3.438, 'wayTooCloseThreshold': 70.268,
                             'tooCloseThreshold': 0.008, 'tooFarAwayThreshold': 2039.184, 'wayTooCloseValue': 394.23,
                             'tooCloseValue': 195.778, 'dangerZoneMultiplier': 1.123,
                             'dangerZoneMiddleMapNodeMultiplier': 0.757, 'ghostInDangerZoneMultiplier': 0.0,
                             'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 5.169, 'edgeMultiplier': 4.045}),
            WeightContainer({'fleeThreshold': 0.142, 'pelletLevelDistance': 2.699, 'wayTooCloseThreshold': 60.868,
                             'tooCloseThreshold': 0.263, 'tooFarAwayThreshold': 1769.249, 'wayTooCloseValue': 864.227,
                             'tooCloseValue': 47.85, 'dangerZoneMultiplier': 0.485,
                             'dangerZoneMiddleMapNodeMultiplier': 0.043, 'ghostInDangerZoneMultiplier': 0.002,
                             'closestGhostMultiplier': 0.579, 'ghostIsCloserMultiplier': 8.302, 'edgeMultiplier': 2.0}),
            WeightContainer({'fleeThreshold': 0.153, 'pelletLevelDistance': 2.144, 'wayTooCloseThreshold': 64.359,
                             'tooCloseThreshold': 0.34, 'tooFarAwayThreshold': 1195.206, 'wayTooCloseValue': 2600.674,
                             'tooCloseValue': 123.482, 'dangerZoneMultiplier': 0.407,
                             'dangerZoneMiddleMapNodeMultiplier': 0.873, 'ghostInDangerZoneMultiplier': 0.0,
                             'closestGhostMultiplier': 0.275, 'ghostIsCloserMultiplier': 8.302,
                             'edgeMultiplier': 3.175}),
            WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 20.577,
                             'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 1979.009, 'wayTooCloseValue': 3423.479,
                             'tooCloseValue': 1355.534, 'dangerZoneMultiplier': 0.005,
                             'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.99,
                             'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.612,
                             'edgeMultiplier': 2.109}),
            WeightContainer({'fleeThreshold': 0.035, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 20.949,
                             'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 1979.009, 'wayTooCloseValue': 4372.183,
                             'tooCloseValue': 1363.13, 'dangerZoneMultiplier': 0.005,
                             'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431,
                             'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.612,
                             'edgeMultiplier': 1.237}),
            WeightContainer({'fleeThreshold': 0.008, 'pelletLevelDistance': 0.702, 'wayTooCloseThreshold': 25.613,
                             'tooCloseThreshold': 0.003, 'tooFarAwayThreshold': 4857.633, 'wayTooCloseValue': 412.091,
                             'tooCloseValue': 250.258, 'dangerZoneMultiplier': 1.431,
                             'dangerZoneMiddleMapNodeMultiplier': 0.458, 'ghostInDangerZoneMultiplier': 0.0,
                             'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 10.304, 'edgeMultiplier': 2.237})
        ]

        # generate random population from the default weight container from the agent
        population = [defaultWeightContainer]
        population += weightList
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateAll(defaultWeightContainer, 5)
            population.append(newWeightContainer)

        # print start population
     #   for pop in population:
     #        print(pop)
      #  exit()

        generationTestingTime = []

        constArgs = (agentClass, gameCount)

        print("\n\n------------- Starting new genetic tournament -------------")
        print(f"Starting at: {getCurrentTimestamp()}")
        print(f"Agent: {agentClass.__name__}")
        print(f"{totalGameCount} games will be played over "
              f"{generationCount} generations with a population size of {populationSize}.")
        print(f"Each agent will be tested on {gameCount} games, using {cpuCount} CPU cores.")

        for generation in range(generationCount):
            print(f"\n\n------------- Generation {generation + 1} of {generationCount} -------------")
            print(f"Started at: {getCurrentTimestamp()}")
            print(f"Mutation rate: {currentMutationRate}")

            # don't remove thjs line!
            stats = []

            start_time = time.time()
            with multiprocessing.Pool(processes=cpuCount) as pool:
                stats = pool.starmap(TournamentRunner.fitnessFunctionWrapper,
                                     [(member, constArgs) for member in population])
            end_time = time.time()

            for j in range(populationSize):
                population[j].addFitness(stats[j]['combinedScore'])

            # sort population by fitness (with stats)
            paired_sorted_lists = sorted(zip(population, stats), key=lambda x: x[0].getFitness(), reverse=True)
            population, stats = zip(*paired_sorted_lists)
            population = list(population)
            stats = list(stats)

            # print stats
            generationTimeTaken = end_time - start_time
            generationTestingTime.append(generationTimeTaken)
            if len(generationTestingTime) > 5:
                generationTestingTime.pop(0)

            averageGenerationTimeTaken = sum(generationTestingTime) / len(generationTestingTime)
            estimatedSecondsLeft = (generationCount - generation) * averageGenerationTimeTaken

            print("\nAgent      Fitness  Avg Lvl Comp  Survived")
            for i in range(populationSize):
                print("{:<10} {:<8} {:<13} {:<8}".format(
                    f"{i + 1} of {populationSize}",
                    population[i].getFitness(),
                    stats[i]['averageLevelsCompleted'],
                    population[i].getGenerationsSurvived()
                ))
            print(f"Generation took:     {secondsToTime(generationTimeTaken)}")
            print(f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
            print(f"Current runtime:     {secondsToTime(time.time() - tournamentStartTime)}")
            print(f"Progress:            {round(generation / (generationCount / 100), 1)}%")

            bestOfEachGenerations.append(population[0])

            print("\nBest of each generations:")
            print("Generation Fitness Survived")
            for j in range(len(bestOfEachGenerations)):
                print("{:<10} {:<7} {:<8}".format(
                    f"Gen {j + 1}",
                    bestOfEachGenerations[j].getFitness(),
                    bestOfEachGenerations[j].getGenerationsSurvived()
                ))

            # add all members of population to all members
            allMembers += population
            # remove duplicates
            allMembers = list(set(allMembers))
            # sort all members by fitness
            allMembers.sort(key=lambda x: x.getFitness(), reverse=True)

            with open(logFileName, 'w') as file:
                file.write("{:<8} {:<13} {:<200}\n".format('Fitness', 'Gen Survived', 'Weights'))

                for i in range(len(allMembers)):
                    file.write("{:<8} {:<13} {:<200}\n".format(
                        allMembers[i].getFitness(),
                        allMembers[i].getGenerationsSurvived(),
                        str(allMembers[i])
                    ))

            # generate new population
            newPopulation = WeightModifier.generateNewPopulation(
                population=population,
                populationSize=populationSize,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize
            )
            population = newPopulation

            # decrease mutation rate each generation
            # skip first 5 generations
            if generation < 5:
                continue
            currentMutationRate *= mutationRateMultiplier

        print(f"\nThe tournament took: {secondsToTime(time.time() - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")

    @staticmethod
    def fitnessFunctionWrapper(member, args):
        id = random.randint(0, sys.maxsize)

        DebugHelper.disable()
        print(f"############################  {getCurrentTimestamp()}  {id}\n{member}")

        agentClass = args[0]
        gameCount = args[1]

        stats = calculatePerformanceOverXGames(
            agentClass=agentClass,
            weightContainer=member,
            gameCount=gameCount,
            lockDeltaTime=True
        )
        print(f"-------- DONE: {id}")

        return stats


if __name__ == "__main__":
    DebugHelper.disable()
    TournamentRunner.startNewTournament(
        agentClass=FirstRealAgent,
        populationSize=50,
        generationCount=40,
        mutationRate=3,
        gameCount=70,
        cpuCount=4  # multiprocessing.cpu_count()
    )
