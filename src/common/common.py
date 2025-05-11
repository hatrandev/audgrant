import numpy as np
import random
from src.config.simulation_config import ExperimentConfig
from src.common.logger import logger


class Common_RNG:
    def __init__(self):
        """
        Initialize the Common class with a base seed.

        :param seed: Base seed for reproducibility.
        """
        self.seed = ExperimentConfig.seed


    def get_rng_for_person(self, person_id):
        """
        Get a reproducible RNG for a given person based on the base seed and the person ID.
        
        :param person_id: Unique identifier for the person.
        :return: np.random.Generator object.
        """
        seed = hash((self.seed, person_id)) % (2**32)
        return np.random.default_rng(seed)