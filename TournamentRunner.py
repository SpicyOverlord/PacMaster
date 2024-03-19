import random
import sys
import time
from datetime import datetime
import multiprocessing
import os
from multiprocessing import TimeoutError

import numpy as np

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
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
    def startNewTournament(agentClass: type[IAgent], populationSize: int, generationCount: int,
                           freeGenerationCount: int, savePercentage: int, mutationRate: float,
                           gameCount: int, cpuCount: int, timeoutSeconds: int):
        tournamentStartTime = time.time()

        logFileName = f"Tournaments/{getCurrentTimestamp()}_{agentClass.__name__}.txt"

        allMembers = []

        totalGameCount = populationSize * generationCount * gameCount

        bestOfEachGenerations = []

        poolSize = max(int(populationSize * 0.2), 2)
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / (generationCount - freeGenerationCount))) * (1 / mutationRate) ** (
                1 / (generationCount - freeGenerationCount))

        defaultWeightContainer = agentClass.getDefaultWeightContainer()

        # generate random population from the default weight container from the agent
        # prePopulation = []
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 16.024, 'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 2069.434, 'wayTooCloseValue': 3089.918, 'tooCloseValue': 1456.791, 'dangerZoneMultiplier': 0.005, 'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431, 'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.208, 'edgeMultiplier': 3.232}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.168, 'pelletLevelDistance': 3.438, 'wayTooCloseThreshold': 70.268, 'tooCloseThreshold': 0.008, 'tooFarAwayThreshold': 2039.184, 'wayTooCloseValue': 394.23, 'tooCloseValue': 195.778, 'dangerZoneMultiplier': 1.123, 'dangerZoneMiddleMapNodeMultiplier': 0.757, 'ghostInDangerZoneMultiplier': 0.0, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 5.169, 'edgeMultiplier': 4.045}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.45, 'pelletLevelDistance': 312.675, 'wayTooCloseThreshold': 1.59, 'tooCloseThreshold': 72.969, 'tooFarAwayThreshold': 2956.632, 'wayTooCloseValue': 2410.48, 'tooCloseValue': 167.061, 'dangerZoneMultiplier': 3.798, 'dangerZoneMiddleMapNodeMultiplier': 1.073, 'ghostInDangerZoneMultiplier': 12.56, 'closestGhostMultiplier': 83.481, 'ghostIsCloserMultiplier': 10.784, 'edgeMultiplier': 0.048}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.008, 'pelletLevelDistance': 0.702, 'wayTooCloseThreshold': 25.613, 'tooCloseThreshold': 0.003, 'tooFarAwayThreshold': 4857.633, 'wayTooCloseValue': 412.091, 'tooCloseValue': 250.258, 'dangerZoneMultiplier': 1.431, 'dangerZoneMiddleMapNodeMultiplier': 0.458, 'ghostInDangerZoneMultiplier': 0.0, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 10.304, 'edgeMultiplier': 2.237}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 2.16801, 'pelletLevelDistance': 198.84966, 'wayTooCloseThreshold': 0.88123, 'tooCloseThreshold': 13.33625, 'tooFarAwayThreshold': 3493.55815, 'wayTooCloseValue': 1097.04523, 'tooCloseValue': 125.08157, 'dangerZoneMultiplier': 0.48795, 'dangerZoneMiddleMapNodeMultiplier': 9.13484, 'ghostInDangerZoneMultiplier': 7.81239, 'closestGhostMultiplier': 2.74904, 'ghostIsCloserMultiplier': 1.95321, 'edgeMultiplier': 3.87434}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.32246, 'pelletLevelDistance': 77.53889, 'wayTooCloseThreshold': 98.53012, 'tooCloseThreshold': 30.01019, 'tooFarAwayThreshold': 2070.39002, 'wayTooCloseValue': 579.86987, 'tooCloseValue': 415.81436, 'dangerZoneMultiplier': 4.13483, 'dangerZoneMiddleMapNodeMultiplier': 0.49617, 'ghostInDangerZoneMultiplier': 3.33331, 'closestGhostMultiplier': 2.33804, 'ghostIsCloserMultiplier': 1.69757, 'edgeMultiplier': 4.61846}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.39279, 'pelletLevelDistance': 88.72579, 'wayTooCloseThreshold': 200.40252, 'tooCloseThreshold': 4022.7341, 'tooFarAwayThreshold': 1.38749, 'wayTooCloseValue': 1442.67563, 'tooCloseValue': 26916.95258, 'dangerZoneMultiplier': 11.50758, 'dangerZoneMiddleMapNodeMultiplier': 0.17607, 'ghostInDangerZoneMultiplier': 0.39696, 'closestGhostMultiplier': 10.04529, 'ghostIsCloserMultiplier': 0.26899, 'edgeMultiplier': 1.83389}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.01119, 'pelletLevelDistance': 2.83253, 'wayTooCloseThreshold': 32.68235, 'tooCloseThreshold': 8e-05, 'tooFarAwayThreshold': 1219.81699, 'wayTooCloseValue': 352.64291, 'tooCloseValue': 87.99661, 'dangerZoneMultiplier': 8.68754, 'dangerZoneMiddleMapNodeMultiplier': 0.00206, 'ghostInDangerZoneMultiplier': 0.0, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 3.11343, 'edgeMultiplier': 1.75577}))
        # prePopulation.append(WeightContainer({'fleeThreshold': 0.01012, 'pelletLevelDistance': 3.40838, 'wayTooCloseThreshold': 38.31477, 'tooCloseThreshold': 0.003, 'tooFarAwayThreshold': 2043.80368, 'wayTooCloseValue': 597.86046, 'tooCloseValue': 654.69161, 'dangerZoneMultiplier': 9.37635, 'dangerZoneMiddleMapNodeMultiplier': 0.00193, 'ghostInDangerZoneMultiplier': 34.82505, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 15.93602, 'edgeMultiplier': 1.9445}))
        # prePopulation.append(defaultWeightContainer)
        population = []
        # population.extend(prePopulation)

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
            # with multiprocessing.Pool(processes=cpuCount) as pool:
            #     stats = pool.starmap(TournamentRunner.fitnessFunctionWrapper,
            #                          [(member, constArgs) for member in population])
            stats = TournamentRunner.parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount)

            end_time = time.time()

            for j in range(populationSize):
                if stats[j] is None:
                    # print(f"Agent {j + 1} of {populationSize} timed out!")
                    population[j].addFitness(0)
                    continue

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
                savePercentage=savePercentage,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize,
                freeGenerationCount=freeGenerationCount,
                generation=generation
            )
            population = newPopulation

            # decrease mutation rate each generation
            # skip first 5 generations
            if generation < freeGenerationCount:
                continue
            currentMutationRate *= mutationRateMultiplier

        print(f"\nThe tournament took: {secondsToTime(time.time() - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")

    @staticmethod
    def parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount):
        with multiprocessing.Pool(processes=cpuCount) as pool:
            results = [pool.apply_async(TournamentRunner.fitnessFunctionWrapper, (member, constArgs)) for member in population]
            finished_stats = []

            for i in range(len(results)):
                try:
                    finished_stats.append(results[i].get(timeout=timeoutSeconds))
                except multiprocessing.TimeoutError:
                    print(f"An agent timed out!")
                    finished_stats.append(GameStats.getEmpty())

            return finished_stats

    @staticmethod
    def fitnessFunctionWrapper(member, args):
        DebugHelper.disable()

        agentClass = args[0]
        gameCount = args[1]

        stats = calculatePerformanceOverXGames(
            agentClass=agentClass,
            weightContainer=member,
            gameCount=gameCount,
            lockDeltaTime=True
        )

        return stats


if __name__ == "__main__":
    DebugHelper.disable()
    TournamentRunner.startNewTournament(
        agentClass=FirstRealAgent,
        populationSize=40,
        freeGenerationCount=10,
        generationCount=40,
        savePercentage=10,
        mutationRate=3,
        gameCount=3,
        cpuCount=4,  # multiprocessing.cpu_count(),
        timeoutSeconds=30*60
    )
