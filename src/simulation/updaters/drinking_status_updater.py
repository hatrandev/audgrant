import pandas as pd
import numpy as np
from collections import defaultdict
from src.common.logger import logger
from src.config.simulation_config import ExperimentConfig
from src.common.constants import InitializationConstants


class DrinkingStatusUpdater:

    def __init__(self, population_df, drinking_transition_lookup_df):

        self.population_df = population_df
        self.transition_df = drinking_transition_lookup_df
        self.seed = ExperimentConfig.seed

    def update_drinking_status(self):

        """
        Update the population DataFrame by determining drinking status transitions based on a 
        transition probability lookup table. This method assigns age groups, merges the population 
        DataFrame with a transition DataFrame to determine the probability of transitioning between 
        drinking stages, and uses a random number generator to sample outcomes for each individual. 
        The drinking stage of each individual is updated accordingly.
        :return: The updated population DataFrame with the 'Drinking_Stage' modified based on 
             transition probabilities.
        """

        # Step 1: Assign age group (vectorized)
        self.population_df['Age_Group'] = pd.cut(
            self.population_df['Age'],
            bins=[0, 17, 35, 50, float('inf')],
            labels=["0-17", "18-34", "35-50", "51+"]
        )

        # Step 2: Merge with transition probabilities
        df = pd.merge(
            self.population_df,
            self.transition_df,
            how='left',
            on=['Age_Group', 'Composite', 'Drinking_Stage']
        )

        # Step 3: Extract necessary columns
        #ids = df[InitializationConstants.ID_KEY].to_numpy()
        current_stages = df['Drinking_Stage'].to_numpy()
        prob_column = df['Drinking_Transition_Probability'].to_numpy()

        updated_stages = current_stages.copy()

        # Step 4: Group rows by unique transition dicts
        grouped_indices = defaultdict(list)
        for i, prob in enumerate(prob_column):
            if isinstance(prob, dict):
                key = tuple(sorted(prob.items()))
                grouped_indices[key].append(i)

        # Step 5: Sample outcomes for each group
        for prob_key, indices in grouped_indices.items():
            stages, probs = zip(*prob_key)
            stages = np.array(stages)
            probs = np.array(probs, dtype=np.float64)

            # Use one RNG per group
            group_seed = abs(hash(prob_key)) % (2**32)
            rng = np.random.default_rng(group_seed)

            samples = rng.choice(stages, p=probs, size=len(indices))
            updated_stages[indices] = samples

        # Step 6: Assign and clean up
        df['Drinking_Stage'] = updated_stages
        df.drop(columns=['Age_Group', 'Drinking_Transition_Probability'], inplace=True)
        logger.info("Drinking status updated successfully.")
        return df
