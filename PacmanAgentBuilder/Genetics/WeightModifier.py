import random

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer


class WeightModifier:
    """
    This class contains static methods for modifying and creating WeightContainers.
    This is used in the genetic algorithm to mutate, combine and create new WeighContainers.
    """
    @staticmethod
    def mutateRandom(weights: WeightContainer, mutationRate: float):
        """
        This method mutates the weights by a random amount (max mutationRate).
        :param weights: The WeightContainer to mutate.
        :param mutationRate: The maximum amount to mutate the weights.
        :return: The new mutated WeightContainer.
        """
        mutation = WeightContainer()

        for key, value in weights.items():
            # when the mutationRate is low, the change of mutation is low
            if random.random() < mutationRate:
                mutateDistance = random.uniform(-1, 1) * mutationRate
                mutatedValue = value + value * mutateDistance

                # stop weights from becoming negative
                if mutatedValue < 0:
                    mutatedValue *= -1
            else:
                mutatedValue = value

            mutation.add(key, round(mutatedValue, 5))

        return mutation

    @staticmethod
    def randomSelectCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        """
        This method combines two WeightContainers by randomly selecting the weights from one of the two,
        one weight at a time.
        :param weightsA: The first WeightContainer parent.
        :param weightsB: The second WeightContainer parent.
        :return: The new WeightContainer offspring that is a combination of the parents.
        """
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        offspring = WeightContainer()

        for key, value in weightsA.items():
            # 50% chance of selecting the weight from either parent
            if random.random() < 0.5:
                offspring.add(key, value)
            else:
                offspring.add(key, weightsB.get(key))

        return offspring

    @staticmethod
    def tournamentSelectParent(weightsList: list[WeightContainer], poolSize: int) -> WeightContainer:
        """
        This method selects a parent from a list of WeightContainers by using Tournament Selection.
        This means that the higher a WeightContainer's fitness is, the higher the chance of it being selected.
        :param weightsList: The list of WeightContainers to select from (population).
        :param poolSize: The size of the tournament pool.
        :return: The selected WeightContainer parent.
        """

        tournament = []

        for i in range(poolSize):
            tournament.append(random.choice(weightsList))

        return max(tournament, key=lambda x: x.getFitness())

    @staticmethod
    def checkSameKeySet(weightsA: WeightContainer, weightsB: WeightContainer) -> bool:
        """
        This method checks if two WeightContainers have the same keys.
        It's just a precaution to avoid errors.
        :param weightsA: The first WeightContainer.
        :param weightsB: The second WeightContainer.
        :return: True if the WeightContainers have the same keys. Throws an error if not.
        """
        if set(weightsA.keys()) != set(weightsB.keys()):
            raise ValueError("Weights does not have the same keys")

        return True

    @staticmethod
    def generateNewPopulation(population: list[WeightContainer], populationSize: int, freeGenerationCount: int,
                              savePercentage: int, currentMutationRate: float,
                              poolSize: int, generation: int) -> list[WeightContainer]:
        """
        This method generates a new population from a previous population.
        It saves the top x% of the previous generation and creates new children from the rest using Tournament Selection.
        :param population: The previous generation of WeightContainers.
        :param populationSize: The size of the population that will be created.
        :param freeGenerationCount: if the current generation number is less than this, the top x% of the previous generation will not be saved.
        :param savePercentage: The percentage of the previous generation that will be saved.
        :param currentMutationRate: The current mutation rate used to mutate the new population.
        :param poolSize: The size of the tournament pool used in Tournament Selection.
        :param generation: The current generation number.
        :return: The new population of WeightContainers.
        """
        # x% of the new population will be the top x% of the previous generation
        # only if the current generation is greater than the freeGenerationCount
        newPopulation = []
        if generation >= freeGenerationCount:
            newPopulation = population[:int(populationSize * (savePercentage / 100))]

        # The rest of the new population will be a children of the previous generation
        while len(newPopulation) < populationSize:
            parentA = WeightModifier.tournamentSelectParent(population, poolSize)
            parentB = WeightModifier.tournamentSelectParent(population, poolSize)

            child = WeightModifier.randomSelectCombine(parentA, parentB)
            child = WeightModifier.mutateRandom(child, currentMutationRate)

            newPopulation.append(child)

        return newPopulation
