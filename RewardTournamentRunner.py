import random
import time
import multiprocessing
import os
from typing import List

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Qlearning.GameStateData import GameStateData
from PacmanAgentBuilder.Qlearning.RewardFunctions.IRewardFunction import IRewardFunction
from PacmanAgentBuilder.Qlearning.RewardFunctions.MyFirstRewardFunction import MyFirstRewardFunction
from PacmanAgentBuilder.Utils.GameStats import GameStats

from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import calculatePerformanceOverXGames
from PacmanAgentBuilder.Utils.utils import secondsToTime, getCurrentTimestamp

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


class RewardTournamentRunner:
    """
    """

    @staticmethod
    def startNewTournament(rewardFunctionClass: type[IRewardFunction], dataSet: List[GameStateData],
                           populationSize: int,
                           generationCount: int,
                           freeGenerationCount: int, savePercentage: int, mutationRate: float,
                           cpuCount: int, timeoutSeconds: int):
        """
        This method starts a new genetic algorithm tournament for the specified agent.
        :param rewardFunctionClass: The specified agent.
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
        logFileName = f"RewardFunctions/{getCurrentTimestamp()}_{rewardFunctionClass.__name__}.txt"
        allMembers = []
        bestOfEachGenerations = []
        poolSize = max(int(populationSize * 0.1), 2)  # 10% of the population size, but minimum 2

        # calculate the mutation rate multiplier
        # this is done to decrease the mutation rate each generation so the last generations mutation rate is 0.1
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / (generationCount - freeGenerationCount))) * (1 / mutationRate) ** (
                1 / (generationCount - freeGenerationCount))

        # generate start population
        defaultWeightContainer = rewardFunctionClass.getDefaultWeightContainer()
        population = []
        # each member of the population is a very mutated version of the default weight container
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.FullRandom(defaultWeightContainer, 100)
            population.append(newWeightContainer)

        print("\n\n------------- Starting new genetic tournament -------------")
        print(f"Starting at: {getCurrentTimestamp()}")
        print(f"RewardFunction: {rewardFunctionClass.__name__}")
        print(f"{generationCount} generations with a population size of {populationSize}.")
        print(f"Each reward function will be tested on {len(dataSet)} snapshots, using {cpuCount} CPU cores.")

        for generation in range(generationCount):
            print(f"\n\n------------- Generation {generation + 1} of {generationCount} -------------")
            print(f"Started at: {getCurrentTimestamp()}")
            print(f"Mutation rate: {currentMutationRate}")

            # calculate fitness of population
            start_time = time.time()
            stats = RewardTournamentRunner.parallelFitnessEvaluation(population, rewardFunctionClass, dataSet,
                                                                     timeoutSeconds, cpuCount)
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
    def parallelFitnessEvaluation(population, rewardFunctionClass: type[IRewardFunction], dataSet: List[GameStateData],
                                  timeoutSeconds, cpuCount):
        """
        This method is used to evaluate the fitness of the population in parallel.
        :param population: The population to evaluate.
        :param constArgs: The constant arguments to pass to the fitness function (rewardFunctionClass, gameCount).
        :param timeoutSeconds: The number of seconds to wait for each agent to finish its game before timing out.
        :param cpuCount: The number of CPU cores to use for parallel fitness evaluation.
        :return: A list of the calculated fitness of the population.
        """
        # create a pool of workers
        with multiprocessing.Pool(processes=cpuCount) as pool:
            results = [
                pool.apply_async(RewardTournamentRunner.fitnessFunctionWrapper, (member, rewardFunctionClass, dataSet))
                for member in
                population]
            finished_stats = []

            # get the population's calculated fitness from the pool.
            for i in range(len(results)):
                try:
                    finished_stats.append(results[i].get(timeout=timeoutSeconds))
                except multiprocessing.TimeoutError:
                    print(f"A RewardFunction timed out!")
                    finished_stats.append(GameStats.getEmpty())

            return finished_stats

    @staticmethod
    def fitnessFunctionWrapper(member, rewardFunctionClass: type[IRewardFunction],
                               dataSet: List[GameStateData]) -> float:
        """
        This method is used to wrap the fitness function, so it can be used in the multiprocessing pool.
        :param member: The member to evaluate.
        :return: The calculated fitness of the member.
        """
        # disable the DebugHelper, so it doesn't low down the fitness evaluation
        DebugHelper.disable()

        # calculate the fitness of the member
        try:
            rewardFunction = rewardFunctionClass(member)

            correctGuesses = 0
            for gameStateData in dataSet:
                predictions = gameStateData.generatePredictions()

                maxPredictionReward = -99999.0
                maxPredictionMove = 0
                for prediction in predictions:
                    move, gsData = prediction
                    reward = rewardFunction.calculateReward(gsData)
                    if reward > maxPredictionReward:
                        maxPredictionReward = reward
                        maxPredictionMove = move
                if maxPredictionMove == gameStateData.made_move:
                    correctGuesses += 1

            return round(correctGuesses / (len(dataSet) / 100), 5)


        except Exception as e:
            print(f"An error occurred during fitness evaluation: {e}")
            stats = 0

        return stats


if __name__ == "__main__":
    dataset = []

    DebugHelper.disable()

    # start a new tournament
    RewardTournamentRunner.startNewTournament(
        rewardFunctionClass=MyFirstRewardFunction,  # Specify the agent to be evaluated.
        dataSet=dataset,  # The data set to be used in the reward function.
        populationSize=24,  # The size of the population.
        freeGenerationCount=10,  # generations to skip before save top x% and starting to decrease the mutation rate.
        generationCount=100,  # The number of generations.
        savePercentage=13,  # The top percentile of the population to save each generation.
        mutationRate=1,  # The start mutation rate.
        gameCount=70,  # The number of games each agent will play each generation to calculate its fitness.
        cpuCount=6,  # multiprocessing.cpu_count(),
        timeoutSeconds=30 * 60  # The number of seconds to wait for each agent to finish its game before timing out.
    )
