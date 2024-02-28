import random

from PacMaster.Genetic.WeightContainer import WeightContainer


class Combiner:
    @staticmethod
    def mutate(weights: WeightContainer, mutationRate: float):
        mutation = weights.copy()

        for key, value in mutation.items():
            mutation.setWeight(key, mutation.getWeight(key) * random.uniform(-1, 1) * mutationRate)

        return mutation

    @staticmethod
    def randomCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        # check if the weights have the same keys
        for key, value in weightsA.items():
            if not weightsB.hasWeight(key):
                raise ValueError("Weight with name " + key + " does not exist")
        for key, value in weightsB.items():
            if not weightsA.hasWeight(key):
                raise ValueError("Weight with name " + key + " does not exist")

        # Randomly choose the value from one of the two weights
        childWeights = WeightContainer()
        for key, value in weightsA.items():
            if random.random() < 0.5:
                childWeights.addWeight(key, value)
            else:
                childWeights.addWeight(key, weightsB.getWeight(key))

        return childWeights

    @staticmethod
    def randomBetweenCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        # check if the weights have the same keys
        for key, value in weightsA.items():
            if not weightsB.hasWeight(key):
                raise ValueError("Weight with name " + key + " does not exist")
        for key, value in weightsB.items():
            if not weightsA.hasWeight(key):
                raise ValueError("Weight with name " + key + " does not exist")

        # Randomly choose the value from one of the two weights
        childWeights = WeightContainer()
        for key, value in weightsA.items():
            childWeights.addWeight(key, random.uniform(weightsA.getWeight(key), weightsB.getWeight(key)))

        return childWeights

    @staticmethod
    def tournamentSelectParent(weightsList: list[WeightContainer], poolSize: int) -> WeightContainer:
        tournament = []

        for i in range(poolSize):
            tournament.append(random.choice(weightsList))

        return max(tournament, key=lambda x: x.getFitness())

    @staticmethod
    def sortWeights(weightsList: list[WeightContainer]) -> list[WeightContainer]:
        return sorted(weightsList, key=lambda x: x.getFitness(), reverse=True)
