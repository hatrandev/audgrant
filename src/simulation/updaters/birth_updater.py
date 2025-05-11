from typing import List, Dict
from src.common.constants import ProbabilityRatesColumnNames
from src.config.simulation_config import ExperimentConfig
from src.common.logger import logger
import random
import numpy as np
import pandas as pd


class BirthUpdater:
    def __init__(self, 
                 birth_rate_lookup: Dict[int, float], 
                 male_ratio_lookup: Dict[int, float], 
                 race_lookup: Dict[tuple[int, str], Dict[str, float]]):
        
        logger.info("Initializing BirthUpdater")
        self.birth_rate_lookup = birth_rate_lookup
        self.male_ratio_lookup = male_ratio_lookup
        self.race_lookup = race_lookup
        self.seed = ExperimentConfig.seed
        self.np_random_population = np.random.RandomState(self.seed)
        logger.info(f"Random seed set to {self.seed}")

        
    def compute_new_births(self, population, year: int) -> int:

        """
        Compute the number of new births for a given year based on the total population and birth rate.

        :param total_population: The total population for the year.
        :param year: The year for which to compute the number of new births.
        :return: The computed number of new births as an integer.
        :raises ValueError: If the birth rate for the given year is not found.
        """
        logger.info(f"Computing new births for year {year}")

        new_births = max(0, int(round(len(population) * self.birth_rate_lookup)))

        logger.info(f"Computed {new_births} new births for year {year} with birth rate {self.birth_rate_lookup:.6f}")
        return new_births

    def assign_genders(self, num_births: int, year: int) -> List[str]:
        """
        Assign genders to a specified number of births based on the male-to-female ratio for the given year.

        :param num_births: The number of births to assign genders to.
        :param year: The year for which to determine the male-to-female ratio.
        :return: A list of genders ("Male" or "Female") for the births.
        :raises ValueError: If the male ratio for the given year is not found.
        """
        logger.info(f"Assigning genders for {num_births} births in year {year}")

        genders = self.np_random_population.choice(
            [ProbabilityRatesColumnNames.MALE, ProbabilityRatesColumnNames.FEMALE],
            size=num_births,
            p=[self.male_ratio_lookup, 1 - self.male_ratio_lookup]
        )

        return genders.tolist()

    def assign_races(self, population: List[Dict[str, str]], year: int, num_births: int) -> List[Dict[str, str]]:

        """
        Assign races to each new birth based on the year and gender, updating the population in place.

        :param population: A list of dictionaries representing the new births, each containing 'Gender'.
        :param year: The year for which to assign races.
        :param num_births: The total number of births for the year.
        :return: The updated population with assigned races.
        """
        logger.info(f"Assigning races for {len(population)} births in year {year}")

        male_population = [person for person in population if person["Sex"] == ProbabilityRatesColumnNames.MALE]
        female_population = [person for person in population if person["Sex"] == ProbabilityRatesColumnNames.FEMALE]

        logger.info(f"Gender distribution - Male: {len(male_population)}, Female: {len(female_population)}, "
                    f"Male Percentage: {len(male_population) / num_births:.2%}")

        male_races = self.np_random_population.choice(
            list(self.race_lookup[ProbabilityRatesColumnNames.MALE].keys()),
            size=len(male_population),
            p=list(self.race_lookup[ProbabilityRatesColumnNames.MALE].values())
        )

        female_races = self.np_random_population.choice(
            list(self.race_lookup[ProbabilityRatesColumnNames.FEMALE].keys()),
            size=len(female_population),
            p=list(self.race_lookup[ProbabilityRatesColumnNames.FEMALE].values())
        )

        logger.info(f"Assigning races to male population")
        for person, race in zip(male_population, male_races):
            person["Race"] = race
            person["Drinking_Stage"] = "Abs"

        logger.info(f"Assigning races to female population")
        for person, race in zip(female_population, female_races):
            person["Race"] = race
            person["Drinking_Stage"] = "Abs"

        logger.info(f"Successfully assigned races for {len(population)} births in year {year}")
        return population

    def generate_new_births(self, population: int, year: int) -> List[Dict[str, str]]:
        """
        Generate a list of new births for a specified year based on the total population and demographic data.

        This method calculates the number of new births for the given year, determines their genders
        using a predefined male-to-female ratio, and assigns races to the newborns. Each newborn is
        represented as a dictionary containing their age and gender, with race information added.

        :param total_population: The total population for the year.
        :param year: The year for which to generate new births.
        :return: A list of dictionaries representing the new births, each containing 'Age', 'Gender', and 'Race'.
        :raises RuntimeError: If an error occurs during the generation of new births.
        """
        logger.info(f"Starting generation of new births for year {year}")

        try:
            # Compute the number of new births based on the total population and birth rate
            num_births = self.compute_new_births(population, year)
            logger.info(f"Calculated {num_births} new births for year {year} "
                        f"(Proportion: {num_births / len(population):.2%})")

            # Assign genders to the newborns
            genders = self.assign_genders(num_births, year)
            new_births = [{"Age": 0, "Sex": gender, 'Alive': True, 'Immigration': False} for gender in genders]

            # Assign races to the newborns
            new_births = self.assign_races(new_births, year, num_births)
            logger.info(f"Successfully generated {len(new_births)} new births for year {year}")

            # Convert to pandas dataframe for efficiency
            new_births_df = pd.DataFrame(new_births)
            logger.info(f"New births DataFrame created with shape: {new_births_df.shape}")

            # Combine Sex and Race into a single column named 'Compositive'
            new_births_df['Composite'] = new_births_df['Sex'].astype(str) + "_" + \
                                           new_births_df['Race'].astype(str)

            # Generate the ID and Random value for each new birth
            max_id = max(population['ID']) + 1 if 'ID' in population else 1
            new_births_df['ID'] = [i + max_id for i in range(len(new_births_df))]

            # Drop the individual columns
            new_births_df.drop(columns=['Sex', 'Race'], inplace=True)
            logger.info("Combined Sex, Race into a single column and removed the individual columns.")
            return new_births_df

        except Exception as e:
            logger.error(f"An error occurred while generating new births for year {year}: {e}")
            raise RuntimeError(f"Failed to generate new births for year {year}") from e
