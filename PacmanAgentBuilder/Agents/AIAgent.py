from time import sleep

import joblib
import numpy as np
import pygame
import tensorflow as tf
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
from sklearn.preprocessing import StandardScaler

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.Snapshot import Snapshot
from PacmanAgentBuilder.Utils.observation import Observation
from Pacman_Complete.constants import *


class AIAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

        self.scaler = joblib.load('Models/scalerOver5Levels.save')
        self.model = tf.keras.models.load_model('Models/Over5Levels.keras')

    def calculateNextMove(self, obs: Observation):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            sleep(0.1)
            return UP
        if key_pressed[K_DOWN]:
            sleep(0.1)
            return DOWN
        if key_pressed[K_LEFT]:
            sleep(0.1)
            return LEFT
        if key_pressed[K_RIGHT]:
            sleep(0.1)
            return RIGHT

        snapshot = Snapshot(obs)
        snapShotArray = snapshot.getInputArray()
        normalizedSnapShotArray = self.scaler.transform([snapShotArray])

        predictions = self.model.predict(normalizedSnapShotArray, verbose=0)
        predicted_action = np.argmax(predictions, axis=1)[0]

        if predicted_action == 0:
            return UP
        elif predicted_action == 1:
            return DOWN
        elif predicted_action == 2:
            return LEFT
        elif predicted_action == 3:
            return RIGHT
        return STOP
