import random


class WeightContainer:
    """
    This class is a container for weights. It is used to store the weights of the agents,
    as well as the fitness that is used in the genetic algorithm.

    It is basically just a dictionary with some extra functionality.
    """

    def __init__(self, weightDict: dict[str, float] = None):
        self.__weightDict__ = weightDict if weightDict is not None else {}
        self.__fitness__ = []

    def addFitness(self, fitness: float):
        self.__fitness__.append(fitness)

    def getFitness(self) -> float:
        if len(self.__fitness__) == 0:
            return 0
        return round(sum(self.__fitness__) / len(self.__fitness__), 3)

    def getGenerationsSurvived(self) -> int:
        return len(self.__fitness__)

    def hasFitness(self) -> bool:
        return len(self.__fitness__) != 0

    def copy(self) -> 'WeightContainer':
        newWeights = WeightContainer()
        for key, value in self.__weightDict__.items():
            newWeights.add(key, value)
        return newWeights

    def add(self, name: str, weight: float):
        if name in self.__weightDict__:
            raise ValueError("Weight with name " + name + " already exists")

        self.__weightDict__[name] = weight

    def get(self, name: str) -> float:
        return self.__weightDict__[name]

    def hasWeight(self, name: str) -> bool:
        return name in self.__weightDict__

    def items(self):
        return self.__weightDict__.items()

    def keys(self):
        return self.__weightDict__.keys()

    def __str__(self):
        return str(self.__weightDict__)

    def __eq__(self, other):
        if not isinstance(other, WeightContainer):
            return False
        return self.__weightDict__ == other.__weightDict__

    def __hash__(self):
        return hash(str(self.__weightDict__))
