import random
import time
import multiprocessing
import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.GameStats import GameStats

from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import calculatePerformanceOverXGames
from PacmanAgentBuilder.Utils.utils import secondsToTime, getCurrentTimestamp

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


class TournamentRunner:
    """
    This class is used to run a genetic algorithm tournament for a specified agent.
    It is used to find the (hopefully) optimal weights for the agent.
    """

    @staticmethod
    def startNewTournament(agentClass: type[IAgent], populationSize: int, generationCount: int,
                           freeGenerationCount: int, savePercentage: int, mutationRate: float,
                           gameCount: int, cpuCount: int, timeoutSeconds: int):
        """
        This method starts a new genetic algorithm tournament for the specified agent.
        :param agentClass: The specified agent.
        :param populationSize: The size of the population.
        :param generationCount: The number of generations.
        :param freeGenerationCount: The number of generations to skip before save top x% and starting to decrease the mutation rate.
        :param savePercentage: The top percentile of the population to save each generation.
        :param mutationRate: The start mutation rate.
        :param gameCount: The number of games each agent will play each generation to calculate its fitness.
        :param cpuCount: The number of CPU cores to use for parallel fitness evaluation.
        :param timeoutSeconds: The number of seconds to wait for each agent to finish its game before timing out.
        :return: None
        """

        # set some variables that is used in the tournament
        tournamentStartTime = time.time()
        logFileName = f"Tournaments/{getCurrentTimestamp()}_{agentClass.__name__}.txt"
        allMembers = []
        bestOfEachGenerations = []
        totalGameCount = populationSize * generationCount * gameCount
        poolSize = max(int(populationSize * 0.1), 2)  # 10% of the population size, but minimum 2
        constArgs = (agentClass, gameCount)

        # calculate the mutation rate multiplier
        # this is done to decrease the mutation rate each generation so the last generations mutation rate is 0.1
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / (generationCount - freeGenerationCount))) * (1 / mutationRate) ** (
                1 / (generationCount - freeGenerationCount))

        # generate start population
        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        population = []
        # each member of the population is a very mutated version of the default weight container
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateRandom(defaultWeightContainer, 5)
            newWeightContainer = WeightModifier.mutateRandom(newWeightContainer, 2)
            # newWeightContainer = WeightModifier.mutateRandom(newWeightContainer, 2)
            # newWeightContainer = WeightModifier.mutateRandom(newWeightContainer, 2)
            # newWeightContainer = WeightModifier.mutateRandom(newWeightContainer, 2)
            population.append(newWeightContainer)

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

            # calculate fitness of population
            start_time = time.time()
            stats = TournamentRunner.parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount)
            end_time = time.time()

            # add the calculated fitness to each member of the population
            for j in range(len(population)):
                # if the agent timed out, set its fitness to 0
                if stats[j] is None:
                    population[j].addFitness(0)
                    continue

                population[j].addFitness(stats[j]['combinedScore'])

            # sort population by fitness (with stats)
            paired_sorted_lists = sorted(zip(population, stats), key=lambda x: x[0].getFitness(), reverse=True)
            population, stats = zip(*paired_sorted_lists)
            population = list(population)
            stats = list(stats)

            # calculate the time taken to calculate the fitness of the generation
            currentRuntime = time.time() - tournamentStartTime
            progress = (generation + 1) / generationCount * 100
            estimatedSecondsLeft = currentRuntime / progress * (100 - progress)
            generationTimeTaken = end_time - start_time

            # print the stats of the generation
            print("\nAgent      Fitness  Avg Lvl Comp  Survived")
            for i in range(len(population)):
                print("{:<10} {:<8} {:<13} {:<8}".format(
                    f"{i + 1} of {len(population)}",
                    population[i].getFitness(),
                    stats[i]['averageLevelsCompleted'],
                    population[i].getGenerationsSurvived()
                ))
            print(f"Generation took:     {secondsToTime(generationTimeTaken)}")
            print(f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
            print(f"Current runtime:     {secondsToTime(currentRuntime)}")
            print(f"Progress:            {round(progress, 1)}%")

            # save the best of the generation
            bestOfEachGenerations.append(population[0])
            # print the best of the generation
            print("\nBest of each generations:")
            print("Generation Fitness Survived")
            for j in range(len(bestOfEachGenerations)):
                print("{:<10} {:<7} {:<8}".format(
                    f"Gen {j + 1}",
                    bestOfEachGenerations[j].getFitness(),
                    bestOfEachGenerations[j].getGenerationsSurvived()
                ))

            # write all evaluated members to a log file.
            allMembers += population
            allMembers = list(set(allMembers))
            allMembers.sort(key=lambda x: x.getFitness(), reverse=True)
            with open(logFileName, 'w') as file:
                file.write("{:<8} {:<13} {:<200}\n".format('Fitness', 'Gen Survived', 'Weights'))

                for i in range(len(allMembers)):
                    file.write("{:<8} {:<13} {:<200}\n".format(
                        allMembers[i].getFitness(),
                        allMembers[i].getGenerationsSurvived(),
                        str(allMembers[i])
                    ))

            # generate the new population for the next generation
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
            # skip first x generations
            if generation < freeGenerationCount:
                continue
            currentMutationRate *= mutationRateMultiplier

        print(f"\nThe tournament took: {secondsToTime(time.time() - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")

    @staticmethod
    def parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount):
        """
        This method is used to evaluate the fitness of the population in parallel.
        :param population: The population to evaluate.
        :param constArgs: The constant arguments to pass to the fitness function (agentClass, gameCount).
        :param timeoutSeconds: The number of seconds to wait for each agent to finish its game before timing out.
        :param cpuCount: The number of CPU cores to use for parallel fitness evaluation.
        :return: A list of the calculated fitness of the population.
        """
        # create a pool of workers
        with multiprocessing.Pool(processes=cpuCount) as pool:
            results = [pool.apply_async(TournamentRunner.fitnessFunctionWrapper, (member, constArgs)) for member in
                       population]
            finished_stats = []

            # get the population's calculated fitness from the pool.
            for i in range(len(results)):
                try:
                    finished_stats.append(results[i].get(timeout=timeoutSeconds))
                except multiprocessing.TimeoutError:
                    print(f"An agent timed out!")
                    finished_stats.append(GameStats.getEmpty())

            return finished_stats

    @staticmethod
    def fitnessFunctionWrapper(member, args):
        """
        This method is used to wrap the fitness function, so it can be used in the multiprocessing pool.
        :param member: The member to evaluate.
        :param args: The constant arguments to pass to the fitness function (agentClass, gameCount).
        :return: The calculated fitness of the member.
        """
        # disable the DebugHelper, so it doesn't low down the fitness evaluation
        DebugHelper.disable()

        # calculate the fitness of the member
        agentClass = args[0]
        gameCount = args[1]
        try:
            stats = calculatePerformanceOverXGames(
                agentClass=agentClass,
                weightContainer=member,
                gameCount=gameCount,
                lockDeltaTime=True
            )
        except Exception as e:
            print(f"An error occurred during fitness evaluation: {e}")
            stats = GameStats.getEmpty()

        return stats


if __name__ == "__main__":
    DebugHelper.disable()

    # start a new tournament
    TournamentRunner.startNewTournament(
        agentClass=FinalAgent,  # Specify the agent to be evaluated.
        populationSize=24,  # The size of the population.
        freeGenerationCount=10,  # generations to skip before save top x% and starting to decrease the mutation rate.
        generationCount=100,  # The number of generations.
        savePercentage=13,  # The top percentile of the population to save each generation.
        mutationRate=1,  # The start mutation rate.
        gameCount=70,  # The number of games each agent will play each generation to calculate its fitness.
        cpuCount=6,  # multiprocessing.cpu_count(),
        timeoutSeconds=30 * 60  # The number of seconds to wait for each agent to finish its game before timing out.
    )
