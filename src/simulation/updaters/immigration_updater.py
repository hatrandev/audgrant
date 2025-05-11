from typing import Dict
import numpy as np
import pandas as pd
import random
from src.common.logger import logger
from src.common.common import Common_RNG
from src.common.constants import InitializationConstants
from src.config.simulation_config import ExperimentConfig

class ImmigrationUpdater:
    def __init__(self, 
                 immigration_rate_lookup: Dict[int, float], 
                 age_lookup: Dict[int, Dict[str, float]], 
                 sex_lookup: Dict[int, Dict[str, float]], 
                 race_lookup: Dict[int, Dict[str, Dict[str, float]]],
                 drinking_distribution_df: pd.DataFrame):
        
        """
        Initialize the ImmigrationUpdater with lookup tables for immigration rates, age, sex, and race distributions.

        :param immigration_rate_lookup: A dictionary mapping years to immigration rates.
        :param age_lookup: A dictionary mapping years to age group probabilities.
        :param sex_lookup: A dictionary mapping years to sex probabilities.
        :param race_lookup: A dictionary mapping years to age groups and their race distributions.
        """
        logger.info("Initializing ImmigrationUpdater")
        self.immigration_rate_lookup = immigration_rate_lookup
        self.age_lookup = age_lookup
        self.sex_lookup = sex_lookup
        self.race_lookup = race_lookup
        self.drinking_distribution_df = drinking_distribution_df
        self.common_rng = Common_RNG()
        self.seed = ExperimentConfig.seed
        self.np_random_population = np.random.RandomState(self.seed)

    def _get_age_group_drink_4_groups(self, age):
        """
        Determine the age group for a given age.

        :param age: Age of the individual (0–100).
        :return: Corresponding age group as a string.
        """
        logger.debug(f"Determining age group for age: {age}")

        if 0 <= age <= 17:
            group = "0-17"
        elif 18 <= age <= 34:
            group = "18-34"
        elif 35 <= age <= 54:
            group = "35-54"
        elif age >= 55:
            group = "55 and over"
        else:
            logger.error(f"Invalid age: {age}")
            raise ValueError(f"Invalid age: {age}")

        logger.debug(f"Age {age} falls into group: {group}")
        return group
    
    def _get_age_group_drink_5_groups(self, age):
        """
        Determine the age group for a given age.

        :param age: Age of the individual (0–100).
        :return: Corresponding age group as a string.
        """
        logger.debug(f"Determining age group for age: {age}")

        if 0 <= age <= 17:
            group = "0-17"
        elif 18 <= age <= 24:
            group = "18-24"
        elif 25 <= age <= 34:
            group = "25-34"
        elif 35 <= age <= 54:
            group = "35-54"
        elif age >= 55:
            group = "55 and over"
        else:
            logger.error(f"Invalid age: {age}")
            raise ValueError(f"Invalid age: {age}")

        logger.debug(f"Age {age} falls into group: {group}")
        return group
    
    def _assign_drinking_status(self, drinking_status_dict, random_state):

        """
        Assign a drinking status to an individual based on the provided drinking status distribution.

        :param drinking_status_dict: A dictionary where keys are drinking stages and values are their probabilities.
        :param random_state: A numpy RandomState object for generating random choices.
        :return: The assigned drinking stage.
        """
        stages, probabilities = zip(*drinking_status_dict.items())
        probabilities = np.array(probabilities) / np.sum(probabilities)
        return random_state.choice(stages, p=probabilities)

    def generate_immigration_population(self, population: int, year: int) -> pd.DataFrame:

        """
        Generate the immigration population for a given year based on the total population and lookup tables.

        :param total_population: The total population for the year.
        :param year: The year for which to generate the immigration population.
        :return: A pandas DataFrame representing the immigration population.
        """
        logger.info(f"Generating immigration population for year {year}")

        num_immigrants = max(0, int(round(len(population) * self.immigration_rate_lookup)))
        logger.info(f"Calculated {num_immigrants} immigrants for year {year} with immigration rate {self.immigration_rate_lookup:.6f}")

        # Assign ages
        age_distribution = self.age_lookup['Age']

        ages = self.np_random_population.choice(
            list(age_distribution.keys()),
            size=num_immigrants,
            p=list(age_distribution.values())
        )

        # Assign sexes
        sex_distribution = self.sex_lookup['Age']
        immigration_population = []
        sexes = []
        races = []

        # Assign Age Groups
        for sex in ['Female', 'Male']:
            if sex not in self.race_lookup:
                logger.error(f"Race lookup not found for age group {age}")
                raise ValueError(f"Race lookup not found for age group {age}")
            race_distribution = self.race_lookup[sex]
            age_bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, float('inf')]
            age_labels = [
                "Under 5 years", "5 to 9 years", "10 to 14 years", "15 to 19 years",
                "20 to 24 years", "25 to 29 years", "30 to 34 years", "35 to 39 years",
                "40 to 44 years", "45 to 49 years", "50 to 54 years", "55 to 59 years",
                "60 to 64 years", "65 to 69 years", "70 to 74 years", "75 to 79 years",
                "80 to 84 years", "85 years and over"
            ]
            age_groups = pd.cut(ages, bins=age_bins, labels=age_labels, right=False)
        
        for idx, (age, age_group) in enumerate(zip(ages, age_groups)):
            person_id = population['ID'].max() + idx + 1
            person_rng = self.common_rng.get_rng_for_person(person_id)

            immigration_population.append({
                'Age': age,
                'Alive': True,
                'ID': person_id,
                "Immigration": True,
                "RNG": person_rng
            })

            if age not in sex_distribution:
                logger.error(f"Sex distribution not found for age group {age}")
                raise ValueError(f"Sex distribution not found for age group {age}")
            male_ratio = sex_distribution[age]
            sex = person_rng.choice(
            ["Male", "Female"],
            p=[male_ratio, 1 - male_ratio]
            )
            sexes.append(sex)

            if age_group not in race_distribution:
                logger.error(f"Race distribution not found for age group {age_group}")
                raise ValueError(f"Race distribution not found for age group {age_group}")
            race = person_rng.choice(
                list(race_distribution[age_group].keys()),
                p=list(race_distribution[age_group].values())
            )
            races.append(race)

        # Convert immigration_population to a DataFrame
        immigration_population = pd.DataFrame(immigration_population)

        # Add the "Composite" column
        immigration_population["Composite"] = [f"{sex}_{race}" for sex, race in zip(sexes, races)]

        # Identify unique age groups in the drinking distribution DataFrame
        unique_age_groups = self.drinking_distribution_df[InitializationConstants.AGE_GROUP_KEY].unique()
        logger.info(f"Unique age groups in drinking distribution: {unique_age_groups}")

        # Decide which age group function to use based on unique age groups
        if set(unique_age_groups).issubset({"0-17", "18-34", "35-54", "55 and over"}):
            logger.info("Using 4-group age cutoff for age group determination.")
            self._get_age_group_drink = self._get_age_group_drink_4_groups
        elif set(unique_age_groups).issubset({"0-17", "18-24", "25-34", "35-54", "55 and over"}):
            logger.info("Using 5-group age cutoff for age group determination.")
            self._get_age_group_drink = self._get_age_group_drink_5_groups
        else:
            logger.error(f"Unexpected age groups in drinking distribution: {unique_age_groups}")
            raise ValueError(f"Unexpected age groups in drinking distribution: {unique_age_groups}")

        # Assign drinking stage based on age
        immigration_population[InitializationConstants.AGE_GROUP_KEY] = immigration_population[InitializationConstants.AGE_KEY].apply(self._get_age_group_drink)
        
        # Merge population_df with the drinking distribution DataFrame
        immigration_population = immigration_population.merge(
            self.drinking_distribution_df,
            how='left',
            left_on=[InitializationConstants.AGE_GROUP_KEY, 'Composite'],
            right_on=[InitializationConstants.AGE_GROUP_KEY, 'Composite']
        )
        logger.info("Merged population DataFrame with drinking distribution DataFrame on Age_Group_Key and Composite.")

        # Assign drinking status based on the distribution
        immigration_population[InitializationConstants.DRINKING_STAGE_KEY] = immigration_population.apply(lambda x: self._assign_drinking_status(x[InitializationConstants.DRINKING_STATUS_KEY], 
                                                                                                                                       x[InitializationConstants.RNG_KEY]), axis=1)

        # Drop the individual columns
        immigration_population.drop(columns=[InitializationConstants.DRINKING_STATUS_KEY, 
                                    InitializationConstants.AGE_GROUP_KEY,
                                    InitializationConstants.RNG_KEY], inplace=True)

        logger.info(f"Generated immigration population DataFrame with shape: {immigration_population.shape}")
        return immigration_population
    