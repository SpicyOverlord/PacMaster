import json
import os
import pickle
import time
from typing import List

UNKNOWN_POSITION = -23.456789
DEFAULT_VALUE = [UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION, 0]


class QValueStore:
    basePath = "QLearningData/"

    def __init__(self):
        self.store = {}

        self.gamma = 0.75  # discount factor
        self.baseAlpha = 0.7  # learning rate
        # self.baseRho = 0.2  # exploration rate

        self.baseRho = 0.1


    def size(self):
        return len(self.store)

    def decayValues(self, decayRate: float) -> None:
        self.baseAlpha *= decayRate

    def getVisitedCount(self, stateHash: int) -> int:
        return self.store.setdefault(stateHash, DEFAULT_VALUE.copy())[4]

    def incrementVisitedCount(self, stateHash: int) -> None:
        self.store[stateHash][4] += 1

    def getQValues(self, stateHash: int) -> List[float]:
        return self.store.setdefault(stateHash, DEFAULT_VALUE.copy())[0:4]

    def getQValue(self, stateHash: int, moveIndex: int) -> float:
        if moveIndex > 3:
            raise Exception(f"Invalid action index: {moveIndex}")
        return self.getQValues(stateHash)[moveIndex]

    def getMaxQValue(self, stateHash: int) -> float:
        maxValue = max([qValue if qValue != UNKNOWN_POSITION else -99999 for qValue in self.getQValues(stateHash)])
        if maxValue == -99999:
            return UNKNOWN_POSITION
        return maxValue
        # return max(self.getQValues(stateHash))

    def setQValue(self, stateHash: int, moveIndex: int, reward: float) -> None:
        if moveIndex > 3:
            raise Exception(f"Invalid action index: {moveIndex}")

        if stateHash not in self.store:
            self.store[stateHash] = DEFAULT_VALUE.copy()

        self.incrementVisitedCount(stateHash)

        self.store[stateHash][moveIndex] = reward

    def updateQValue(self, lastStateHash: int, lastActionIndex: int, newStateHash: int, reward: float) -> float:
        if lastActionIndex > 3:
            raise Exception(f"Invalid action index: {lastActionIndex}")

        lastQValue = self.getQValue(lastStateHash, lastActionIndex) + 100
        newStateMaxQValue = self.getMaxQValue(newStateHash)
        visitedCount = self.getVisitedCount(lastStateHash)

        # if reward > 0:
        #     movingAlpha = max(self.baseAlpha - visitedCount * (self.baseAlpha * (1 / self.maxQValueUpdates)), 0.2)
        # else:
        #     movingAlpha = self.baseAlpha
        # newReward = (1 - movingAlpha) * lastQValue + movingAlpha * (reward + self.gamma * newStateMaxQValue)
        newReward = (1 - self.baseAlpha) * lastQValue + self.baseAlpha * (reward + self.gamma * newStateMaxQValue)

        self.setQValue(lastStateHash, lastActionIndex, newReward)

        return newReward

    def getBestMove(self, stateHash: int) -> (int, float):
        qValues = self.getQValues(stateHash)
        maxQValue = max(qValues)
        return qValues.index(maxQValue), maxQValue

    def saveQValuesToJSON(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if not os.path.exists(os.path.dirname(fullPath)):
            os.makedirs(os.path.dirname(fullPath))

        if verbose:
            print(f"Saving json to: '{fullPath}' ...", end="")

        start_time = time.time()
        with open(fullPath, 'w') as file:
            json.dump(self.store, file)
        end_time = time.time()

        time_taken = end_time - start_time
        if verbose:
            print(f" Done! ({round(time_taken, 2)} seconds)")

    def loadQValuesFromJSON(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if verbose:
            print(f"Loading json from: '{fullPath}' ...", end="")
        start_time = time.time()
        try:
            with open(fullPath, 'r') as file:
                self.store = json.load(file)
        except FileNotFoundError:
            print(f"No existing JSON file found at {fullPath}. Starting with an empty Q-value store.")
        end_time = time.time()
        if verbose:
            print(f" Done! ({round(end_time - start_time, 2)} seconds)")

    def saveQValuesToBinary(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if not os.path.exists(os.path.dirname(fullPath)):
            os.makedirs(os.path.dirname(fullPath))

        if verbose:
            print(f"Saving bin to: '{fullPath}' ...", end="")

        start_time = time.time()
        with open(fullPath, 'wb') as file:
            pickle.dump(self.store, file, protocol=pickle.HIGHEST_PROTOCOL)
        end_time = time.time()

        time_taken = end_time - start_time
        if verbose:
            print(f" Done! ({round(time_taken, 2)} seconds)")

    def loadQValuesFromBinary(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if verbose:
            print(f"Loading bin from: '{fullPath}' ...", end="")
        start_time = time.time()
        try:
            with open(fullPath, 'rb') as file:
                self.store = pickle.load(file)
        except FileNotFoundError:
            print(f"No existing binary file found at {fullPath}. Starting with an empty Q-value store.")
        end_time = time.time()
        if verbose:
            print(f" Done! ({round(end_time - start_time, 2)} seconds)")

    # def saveQValuesToCompressedBinary(self, filePath: str, chunk_size: int = 10000) -> None:
    #     fullPath = self.addBasePath(filePath)
    #
    #     if not os.path.exists(os.path.dirname(fullPath)):
    #         os.makedirs(os.path.dirname(fullPath))
    #
    #     print(f"Saving compressed bin to: {fullPath}")
    #
    #     # Split the data into chunks
    #     items = list(self.store.items())
    #     chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    #
    #     # Write each chunk to the file separately
    #     with gzip.open(fullPath, 'wb') as file:
    #         for chunk in chunks:
    #             pickle.dump(dict(chunk), file)
    #
    # def loadQValuesFromCompressedBinary(self, filePath: str) -> None:
    #     fullPath = self.addBasePath(filePath)
    #
    #     try:
    #         with gzip.open(fullPath, 'rb') as file:
    #             while True:
    #                 try:
    #                     chunk = pickle.load(file)
    #                     self.store.update(chunk)
    #                 except EOFError:
    #                     break
    #     except FileNotFoundError:
    #         print(f"No existing compressed binary file found at {fullPath}. Starting with an empty Q-value store.")

    def addBasePath(self, path: str) -> str:
        return self.basePath + path
