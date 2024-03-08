import random
import time
from datetime import datetime
import multiprocessing


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
                           gameCount: int):
        tournamentStartTime = time.time()

        print(f"Starting tournament at {getCurrentTimestamp()}")

        totalGameCount = populationSize * generationCount * gameCount
        finishedGameCount = 0
        print("\n--- Starting new genetic tournament ---")
        print(f"Agent: {agentClass.__name__}")
        print(f"{totalGameCount} games will be played over "
              f"{generationCount} generations with a population size of {populationSize}.")
        print(f"Each agent will be tested on {gameCount} games.")

        bestOfEachGenerations = []

        poolSize = max(int(populationSize * 0.2), 2)
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / generationCount)) * (1 / mutationRate) ** (1 / generationCount)

        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        BestWeightContainer = agentClass.getBestWeightContainer()

        # generate random population from the default weight container from the agent
        population = [defaultWeightContainer]
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateAll(defaultWeightContainer, 5)
            population.append(newWeightContainer)

        # only print start population
        # for pop in population:
        #     print(pop)
        # exit()

        agentTestingTimes = []
        estimatedSecondsLeft = 0
        for generation in range(generationCount):

            print(f"\n------------- Generation {generation + 1} of {generationCount} -------------")
            print(f"Mutation rate: {currentMutationRate}")

            print("Agent        Fitness      Est. time left    Percent Completed")
            for i in range(populationSize):
                start_time = time.time()

                stats = calculatePerformanceOverXGames(
                    agentClass=agentClass,
                    weightContainer=population[i],
                    gameCount=gameCount,
                    lockDeltaTime=True
                )

                end_time = time.time()

                finishedGameCount += gameCount
                population[i].addFitness(stats['combinedScore'])

                print("{:<12} {:<12} {:<17} {:<17}".format(
                    f"{i + 1} of {populationSize}",
                    population[i].getFitness(),
                    secondsToTime(estimatedSecondsLeft),
                    f"{round(finishedGameCount / (totalGameCount / 100), 1)}%"
                ))


                # estimate seconds left until simulation is finished
                timeTaken = end_time - start_time
                agentTestingTimes.append(timeTaken)

                # the average time is only calculated from the last 3 generations of games.
                # this is because as the Agents improve, the games will take longer,
                # and therefore the average will be more accurate if it only includes the most recent games.
                if len(agentTestingTimes) > populationSize * 3:
                    agentTestingTimes.pop(0)

                averageTimeTaken = sum(agentTestingTimes) / len(agentTestingTimes)
                estimatedSecondsLeft = (totalGameCount - finishedGameCount) / gameCount * averageTimeTaken

            # sort population by fitness
            population = WeightModifier.sortByFitness(population)

            bestOfEachGenerations.append(population[0])

            print(f"Finished generation {generation + 1} at: {getCurrentTimestamp()}")
            tournamentEndTime = time.time()
            print(f"Current runtime: {secondsToTime(tournamentEndTime - tournamentStartTime)}")

            # print top 5 of previous generation
            print(f"\nTop 5 of generation {generation + 1}:")
            for j in range(min(5, populationSize)):
                print(population[j])

            print("\nBest of each generations:")
            for i in range(len(bestOfEachGenerations)):
                print(f"Generation {i + 1}: {bestOfEachGenerations[i]}")

            # print all of previous generation
            # for pop in population:
            #     print(pop)

            newPopulation = WeightModifier.generateNewPopulation(
                population=population,
                populationSize=populationSize,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize
            )
            population = newPopulation

            # decrease mutation rate
            # currentMutationRate -= mutationRate / generationCount
            currentMutationRate *= mutationRateMultiplier

        tournamentEndTime = time.time()
        print(f"\nThe tournament took: {secondsToTime(tournamentEndTime - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")


if __name__ == "__main__":
    DebugHelper.disable()
    TournamentRunner.startNewTournament(MyFirstAgent, 5, 3, 2, 1)
