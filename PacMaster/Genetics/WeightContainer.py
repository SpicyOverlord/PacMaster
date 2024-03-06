import random


class WeightContainer:
    def __init__(self, weightDict: dict[str, float] = None):
        self.__weightDict__ = weightDict if weightDict is not None else {}
        self.__fitness__ = []

    def addFitness(self, fitness: float):
        self.__fitness__.append(fitness)

    def getFitness(self) -> float:
        return sum(self.__fitness__) / len(self.__fitness__)

    def hasFitness(self) -> bool:
        return len(self.__fitness__) != 0

    def copy(self) -> 'WeightContainer':
        newWeights = WeightContainer()
        for key, value in self.__weightDict__.items():
            newWeights.addWeight(key, value)
        return newWeights

    def addWeight(self, name: str, weight: float):
        if name in self.__weightDict__:
            raise ValueError("Weight with name " + name + " already exists")

        self.__weightDict__[name] = weight

    def getWeight(self, name: str) -> float:
        return self.__weightDict__[name]

    def hasWeight(self, name: str) -> bool:
        return name in self.__weightDict__

    def items(self):
        return self.__weightDict__.items()

    def keys(self):
        return self.__weightDict__.keys()

    def values(self):
        return self.__weightDict__.values()

    def __str__(self):
        if len(self.__fitness__) != 0:
            return f"Fitness:{self.getFitness()} Survived:{len(self.__fitness__)} Weights:{str(self.__weightDict__)}"
        return f"Weights:{str(self.__weightDict__)}"

    def __eq__(self, other):
        if not isinstance(other, WeightContainer):
            return False
        return self.__weightDict__ == other.__weightDict__
