import random
import time
from collections import Counter

import numpy as np
import pandas as pd

from src.common.logger import logger
from src.config.simulation_config import ExperimentConfig
from src.common.common import Common_RNG
from src.common.constants import InitializationConstants


class PopulationInitializer:
    
    def __init__(self, 
                 age_distribution_dict, 
                 sex_distribution_dict, 
                 race_distribution_dict, 
                 drinking_distribution_df):
        """
        Initialize the PopulationInitializer class.

        :param age_distribution_dict: Dictionary with age groups and their proportions.
        :param sex_distribution_dict: Dictionary with age groups and gender ratios.
        :param race_distribution_dict: Dictionary with (age group, gender) and race proportions.
        :param seed: Optional random seed for reproducibility.
        """
        logger.info("Initializing Population Initializer...")
        self.total_population = ExperimentConfig.INITIAL_TOTAL_POPULATION
        self.age_distribution_dict = age_distribution_dict
        self.sex_distribution_dict = sex_distribution_dict
        self.race_distribution_dict = race_distribution_dict
        self.drinking_distribution_df = drinking_distribution_df
        self.common_rng = Common_RNG()
        self.seed = ExperimentConfig.seed
        self.np_random_population = np.random.RandomState(self.seed)


    def _validate_distributions(self):
        """
        Validate that the input distributions sum to 1 and are well-formed.
        """
        if not np.isclose(sum(self.age_distribution_dict.values()), 1.0):
            logger.error("Age distribution proportions do not sum to 1.")
            raise ValueError("Age distribution proportions must sum to 1.")

        for age, ratio in self.sex_distribution_dict.items():
            if not (0 <= ratio <= 1):
                logger.error(f"Invalid gender ratio for age {age}: {ratio}")
                raise ValueError(f"Gender ratio for age {age} must be between 0 and 1.")

        total_race_proportions = {}
        for _, race_proportions in self.race_distribution_dict.items():
            for race, proportion in race_proportions.items():
                total_race_proportions[race] = total_race_proportions.get(race, 0) + proportion

        if not np.isclose(sum(total_race_proportions.values()), 1.0):
            logger.error("Total race proportions across all groups do not sum to 1.")
            raise ValueError("Total race proportions across all groups must sum to 1.")

    def _get_age_group(self, age):
        """
        Determine the age group for a given age.

        :param age: Age of the individual.
        :return: Corresponding age group as a string.
        """
        logger.debug(f"Determining age group for age: {age}")
        for lower, upper, group in InitializationConstants.AGE_GROUPS:
            if lower <= age <= upper:
                logger.debug(f"Age {age} falls into group: {group}")
                return group

        logger.error(f"Invalid age: {age}")
        raise ValueError(f"Invalid age: {age}")
    
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
        stages, probabilities = zip(*drinking_status_dict.items())
        probabilities = np.array(probabilities) / np.sum(probabilities)
        return random_state.choice(stages, p=probabilities)

    def _adjust_population(self, population, adjustment):
        """
        Adjust the population size to match the configured total population.

        :param population: List of individuals in the population.
        :param adjustment: The number of individuals to add (positive) or remove (negative).
        :return: Adjusted population list.
        """
        population_counter = Counter([person[InitializationConstants.AGE_KEY] for person in population])

        if adjustment > 0:
            logger.debug(f"Adding {adjustment} individuals to the population.")
            age_weights = list(self.age_distribution_dict.values())
            age_choices = list(self.age_distribution_dict.keys())

            new_ages = self.np_random_population.choice(age_choices, size=adjustment, p=age_weights)
            population_counter.update(new_ages)
        elif adjustment < 0:
            logger.debug(f"Removing {abs(adjustment)} individuals from the population.")
            age_weights = list(self.age_distribution_dict.values())
            age_choices = list(self.age_distribution_dict.keys())
            ages_to_remove = self.np_random_population.choice(age_choices, size=abs(adjustment), p=age_weights)
            for age in ages_to_remove:
                if population_counter[age] > 0:
                    population_counter[age] -= 1

        adjusted_population = [{InitializationConstants.AGE_KEY: age} for age, count in population_counter.items() for _ in range(count)]
        return adjusted_population

    def generate_initial_population(self):
        """
        Generate a simulated population with individuals based on age, gender, and race proportions.

        :return: List of dictionaries representing the population.
        """
        logger.info("Generating initial population...")
        logger.info(f"Population generation started with total population: {self.total_population}")
        logger.debug(f"Age distribution: {self.age_distribution_dict}")
        logger.debug(f"Sex distribution: {self.sex_distribution_dict}")
        logger.debug(f"Race distribution: {self.race_distribution_dict}")

        start_time = time.time()  
        population = []

        for age, age_ratio in self.age_distribution_dict.items():
            num_people = int(self.total_population * age_ratio)
            logger.debug(f"Generating {num_people} individuals for age: {age}")
            population.extend([{InitializationConstants.AGE_KEY: age} for _ in range(num_people)])

        if len(population) != self.total_population:
            adjustment = self.total_population - len(population)
            logger.debug(f"Adjusting population size by {adjustment} individuals.")
            population = self._adjust_population(population, adjustment)
        
        assert len(population) == self.total_population, (
            f"Final population size ({len(population)}) does not match the configured total ({self.total_population})."
            )                           

        for index, person in enumerate(population):
            person[InitializationConstants.ID_KEY] = index

        logger.info("Assigned unique ID to each individual in the population.")

        age_counts = {}
        for person in population:
            age = person[InitializationConstants.AGE_KEY]
            if age in age_counts:
                age_counts[age] += 1
            else:
                age_counts[age] = 1

        total_population_count = len(population)

        for age, count in list(age_counts.items())[:3]: 
            proportion = count / total_population_count if total_population_count > 0 else 0
            logger.info(f"Age: {age}, Count: {count}, Proportion: {proportion:.2%}")

        age_gender_counts = {age: Counter() for age in self.sex_distribution_dict.keys()}
        race_counts = {key: Counter() for key in self.race_distribution_dict.keys()}  # Track race counts for specific (age_group, gender)

        for index, person in enumerate(population):
            person[InitializationConstants.ID_KEY] = index
            
            age = person[InitializationConstants.AGE_KEY]
            rng = self.common_rng.get_rng_for_person(person[InitializationConstants.ID_KEY])
            if age in self.sex_distribution_dict:
                gender_ratio = self.sex_distribution_dict[age]
                person[InitializationConstants.GENDER_KEY] = (InitializationConstants.FEMALE if rng.random() < (1 - gender_ratio) else InitializationConstants.MALE)
                logger.debug(f"Assigned gender {person[InitializationConstants.GENDER_KEY]} to individual with age {age}")

            if age in age_gender_counts:
                age_gender_counts[age][person[InitializationConstants.GENDER_KEY]] += 1
            else:
                logger.warning(f"Missing gender ratio for age: {age}. Assigning default ratio of 50%.")
                age_gender_counts[age] = Counter({InitializationConstants.MALE: 0, InitializationConstants.FEMALE: 0})
                age_gender_counts[age][person[InitializationConstants.GENDER_KEY]] += 1

            age_group = self._get_age_group(person[InitializationConstants.AGE_KEY])
            gender = person[InitializationConstants.GENDER_KEY]
            if (age_group, gender) in self.race_distribution_dict:
                race_ratios = self.race_distribution_dict[(age_group, gender)]
                races, probabilities = zip(*race_ratios.items())
                probabilities = np.array(probabilities) / np.sum(probabilities)  # Normalize probabilities
                person[InitializationConstants.RACE_KEY] = rng.choice(races, p=probabilities)
                logger.debug(f"Assigned race {person[InitializationConstants.RACE_KEY]} to individual: {person}")

                race_counts[(age_group, gender)][person[InitializationConstants.RACE_KEY]] += 1
            else:
                logger.error(f"Missing race distribution for age group: {age_group}, gender: {gender}")
                raise KeyError(f"Missing race distribution for age group: {age_group}, gender: {gender}")

            person[InitializationConstants.ALIVE_KEY] = True
            person[InitializationConstants.IMMIGRATION_KEY] = False
            person[InitializationConstants.RNG_KEY] = rng

        for age, gender_count in list(age_gender_counts.items())[:3]:
            total_count = sum(gender_count.values())
            male_count = gender_count.get(InitializationConstants.MALE, 0)
            male_ratio = male_count / total_count if total_count > 0 else 0
            logger.info(
            f"Age: {age}, Total: {total_count}, Male Count: {male_count}, Male Ratio: {male_ratio:.2%}"
            )

        for (age_group, gender), race_count in list(race_counts.items())[:3]:  # Limit to the first 3 (age_group, gender) pairs
            total_count = sum(race_count.values())
            logger.info(f"Age Group: {age_group}, Gender: {gender}, Total: {total_count}")
            for race, count in race_count.items():
                race_ratio = count / total_count if total_count > 0 else 0
                logger.info(f"  Race: {race}, Count: {count}, Proportion: {race_ratio:.2%}")
        
        end_time = time.time()  
        elapsed_time = end_time - start_time
        logger.info(
            f"Population generation complete. Total Population Generated: {len(population)}, "
            f"Configured Initial Population: {self.total_population}, Time Taken: {elapsed_time:.2f} seconds"
        )
        
        population_df = pd.DataFrame(population)
        logger.info(f"Population DataFrame created with shape: {population_df.shape}")

        population_df['Composite'] = population_df[InitializationConstants.GENDER_KEY].astype(str) + "_" + \
                        population_df[InitializationConstants.RACE_KEY].astype(str)
        
        population_df.drop(columns=[InitializationConstants.GENDER_KEY, 
                                    InitializationConstants.RACE_KEY], inplace=True)
        logger.info("Combined Sex, Race, and Immigration into a single column and removed the individual columns.")
        
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


        population_df[InitializationConstants.AGE_GROUP_KEY] = population_df[InitializationConstants.AGE_KEY].apply(self._get_age_group_drink)

        population_df = population_df.merge(
            self.drinking_distribution_df,
            how='left',
            left_on=[InitializationConstants.AGE_GROUP_KEY, 'Composite'],
            right_on=[InitializationConstants.AGE_GROUP_KEY, 'Composite']
        )
        logger.info("Merged population DataFrame with drinking distribution DataFrame on Age_Group_Key and Composite.")

        # Assign drinking status based on the distribution
        population_df[InitializationConstants.DRINKING_STAGE_KEY] = population_df.apply(lambda x: self._assign_drinking_status(x[InitializationConstants.DRINKING_STATUS_KEY], x[InitializationConstants.RNG_KEY]), axis=1)

        population_df.drop(columns=[InitializationConstants.DRINKING_STATUS_KEY, 
                                    InitializationConstants.AGE_GROUP_KEY, 
                                    InitializationConstants.RNG_KEY], inplace=True)

        logger.info("Mapped Age to Age_Group and added Age_Group column to the DataFrame.")
        return population_df
