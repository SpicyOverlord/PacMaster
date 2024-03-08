import random
import time
from datetime import datetime
import multiprocessing
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
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

        totalGameCount = populationSize * generationCount * gameCount

        bestOfEachGenerations = []

        poolSize = max(int(populationSize * 0.2), 2)
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / generationCount)) * (1 / mutationRate) ** (1 / generationCount)

        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        BestWeightContainer = agentClass.getBestWeightContainer()

        # generate random population from the default weight container from the agent
        population = [defaultWeightContainer, BestWeightContainer]
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateAll(defaultWeightContainer, 5)
            population.append(newWeightContainer)

        # only print start population
        # for pop in population:
        #     print(pop)
        # exit()

        generationTestingTime = []

        constArgs = (agentClass, gameCount)

        print("\n\n------------- Starting new genetic tournament -------------")
        print(f"Starting at: {getCurrentTimestamp()}")
        print(f"Agent: {agentClass.__name__}")
        print(f"{totalGameCount} games will be played over "
              f"{generationCount} generations with a population size of {populationSize}.")
        print(f"Each agent will be tested on {gameCount} games, using {cpuCount} CPU cores.\n")

        for generation in range(generationCount):
            print(f"\n------------- Generation {generation + 1} of {generationCount} -------------")
            print(f"Started at: {getCurrentTimestamp()}")
            print(f"Mutation rate: {currentMutationRate}")

            # don't remove!
            stats = []

            start_time = time.time()
            with multiprocessing.Pool(processes=cpuCount) as pool:
                stats = pool.starmap(TournamentRunner.fitnessFunctionWrapper,
                                     [(member, constArgs) for member in population])
            end_time = time.time()

            for j in range(populationSize):
                population[j].addFitness(stats[j]['combinedScore'])

            generationTimeTaken = end_time - start_time
            generationTestingTime.append(generationTimeTaken)
            if len(generationTestingTime) > 5:
                generationTestingTime.pop(0)

            averageGenerationTimeTaken = sum(generationTestingTime) / len(generationTestingTime) / populationSize
            estimatedSecondsLeft = (generationCount - generation) / gameCount * averageGenerationTimeTaken
            # print stats
            print("\nAgent      Fitness     Avg Lvls Completed     Survived")
            for i in range(populationSize):
                print("{:<10} {:<11} {:<22} {:<8}".format(
                    f"{i + 1} of {populationSize}",
                    population[i].getFitness(),
                    stats[i]['averageLevelsCompleted'],
                    population[i].getGenerationsSurvived()
                ))
            print(f"Generation took:     {secondsToTime(generationTimeTaken)}")
            print(f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
            print(f"Current runtime:     {secondsToTime(time.time() - tournamentStartTime)}")
            print(f"Progress:            {round(generation / (generationCount / 100), 1)}%")

            # ----------------------------------

            population = WeightModifier.sortByFitness(population)

            bestOfEachGenerations.append(population[0])

            # print all of previous generation
            # for pop in population:
            #     print(pop)

            # print top 5 of previous generation
            print(f"\nTop 10 of generation {generation + 1}:")
            print("Place Fitness Survived")
            for j in range(min(10, populationSize)):
                print("{:<5} {:<7} {:<8}".format(
                    f"{j + 1}.",
                    population[j].getFitness(),
                    population[j].getGenerationsSurvived()
                ))

            print("\nBest of each generations:")
            print("Generation Fitness Survived")
            for j in range(len(bestOfEachGenerations)):
                print("{:<10} {:<7} {:<8}".format(
                    f"Gen {j + 1}",
                    bestOfEachGenerations[j].getFitness(),
                    bestOfEachGenerations[j].getGenerationsSurvived()
                ))

            newPopulation = WeightModifier.generateNewPopulation(
                population=population,
                populationSize=populationSize,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize
            )
            population = newPopulation

            # decrease mutation rate each generation
            currentMutationRate *= mutationRateMultiplier

        print(f"\nThe tournament took: {secondsToTime(time.time() - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")

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
        agentClass=MyFirstAgent,
        populationSize=20,
        generationCount=5,
        mutationRate=2,
        gameCount=10,
        cpuCount=multiprocessing.cpu_count()
    )
