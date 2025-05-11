import pandas as pd
import numpy as np
import random
from src.common.logger import logger
from src.config.simulation_config import ExperimentConfig
from src.common.common import Common_RNG
from src.common.constants import InitializationConstants

class DeathUpdater:

    def __init__(self, population_df: pd.DataFrame, death_lookup_df: pd.DataFrame):
        self.population_df = population_df
        self.death_lookup_df = death_lookup_df
        self.common_rng = Common_RNG()

    def update_deaths(self):

        """
        Update the population DataFrame by determining deaths based on a death rate lookup table.
        This method merges the population DataFrame with a death lookup DataFrame to determine the 
        probability of death for each individual. It uses a random number generator to simulate 
        whether each individual survives or not based on the death rate. The population DataFrame 
        is updated in place to reflect the changes.
        :return: The updated population DataFrame with the 'Alive' status modified based on death rates.
        """
        
        logger.info("Starting update_deaths method.")

        # Merging population and death lookup dataframes
        logger.debug("Merging population_df with death_lookup_df on ['Composite', 'Age'].")
        merged_df = pd.merge(
            self.population_df,
            self.death_lookup_df,
            on=['Composite', 'Age'],
            how='left'
        )
        rngs = np.random.default_rng(seed=ExperimentConfig.seed)
        merged_df['RNG'] = rngs.random(len(merged_df))

        logger.debug("Applying death update logic based on 'Rate' and 'Alive' columns.")
        alive_mask = merged_df['Alive'] & (merged_df['RNG'] >= merged_df['Rate'])
        merged_df['Alive'] = alive_mask

        logger.debug("Dropping 'Rate' column and updating population_df.")
        self.population_df = merged_df.drop(columns=['Rate', 'Year', 'RNG'])

        logger.info("update_deaths method completed successfully.")
        return self.population_df
