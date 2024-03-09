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

        logFileName = f"Tournaments/{agentClass.__name__}_{getCurrentTimestamp()}.txt"
        allMembers = []

        totalGameCount = populationSize * generationCount * gameCount

        bestOfEachGenerations = []

        poolSize = max(int(populationSize * 0.2), 2)
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / generationCount)) * (1 / mutationRate) ** (1 / generationCount)

        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        BestWeightContainer = agentClass.getBestWeightContainer()

        # generate random population from the default weight container from the agent
        # TODO: remove best!!!!
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

            averageGenerationTimeTaken = sum(generationTestingTime) / len(generationTestingTime) / populationSize
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
        populationSize=50,
        generationCount=40,
        mutationRate=2,
        gameCount=50,
        cpuCount=4  # multiprocessing.cpu_count()
    )
