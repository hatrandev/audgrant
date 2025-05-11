from src.initialization.initializer import Initializer
from src.config.simulation_config import ExperimentConfig
from src.simulation.updaters.birth_updater import BirthUpdater
from src.simulation.updaters.death_updater import DeathUpdater
from src.simulation.updaters.immigration_updater import ImmigrationUpdater
from src.simulation.updaters.drinking_status_updater import DrinkingStatusUpdater
from src.common.logger import logger
import pandas as pd


class SingleYearSimulator:

    def __init__(self, lookup_tables, population, year):
        self.initial_year = ExperimentConfig.INITIAL_YEAR
        self.end_year = ExperimentConfig.END_YEAR
        self.base_path = ExperimentConfig.BASED_PATH
        self.excel_file_name = ExperimentConfig.EXCEL_FILE_NAME
        self.lookup_tables = lookup_tables
        self.population = population
        self.year = year

    def update_births(self):
        """
        Update the population with new births for the current year.
        This method retrieves birth rate, male ratio, and race lookup tables for the specified year
        and uses them to generate new births. The new births are then added to the existing population.
        :raises RuntimeError: If any of the required lookup tables for the current year are not found.
        :raises ValueError: If an error occurs while generating or updating births.
        :return: None
        """
        
        birth_rate_lookup = self.lookup_tables["birth_rate_table"].get(self.year, None)
        if birth_rate_lookup is None:
            raise RuntimeError(f"Birth rate lookup for year {self.year} not found.")
        
        male_ratio_lookup = self.lookup_tables["birth_male_ratio_table"].get(self.year, None)
        if male_ratio_lookup is None:
            raise RuntimeError(f"Sex rate lookup for year {self.year} not found.")
        
        race_lookup = self.lookup_tables["birth_race_lookup_under_5_table"].get(self.year, None)
        if race_lookup is None:
            raise RuntimeError(f"Race lookup for year {self.year} not found.")

        birth_updater = BirthUpdater(
            birth_rate_lookup=birth_rate_lookup,
            male_ratio_lookup=male_ratio_lookup,
            race_lookup=race_lookup
        )

        try:
            new_births = birth_updater.generate_new_births(
                population=self.population,
                year=self.year
            )

            self.population = pd.concat([self.population, new_births], ignore_index=True)

        except RuntimeError as e:
            logger.error(f"Failed to update births: {e}")
            raise ValueError("An error occurred while updating births") from e

    def update_immigration(self):
        """
        Update the population with new immigrants for the current year.
        This method retrieves immigration rate, age, sex, and race lookup tables for the specified year,
        as well as the initial population drinking status distribution. It uses these lookup tables to 
        generate a new immigration population and adds it to the existing population.
        :raises RuntimeError: If any of the required lookup tables for the current year are not found.
        :raises ValueError: If an error occurs while generating or updating immigration.
        :return: None
        """

        try:
            immigration_updater = ImmigrationUpdater(
                immigration_rate_lookup=self.lookup_tables["immigration_rate_lookup"].get(self.year, None),
                age_lookup=self.lookup_tables["immigration_age_lookup"].get(self.year, None),
                sex_lookup=self.lookup_tables["immigration_sex_lookup"].get(self.year, None),
                race_lookup=self.lookup_tables["immigration_race_lookup"].get(self.year, None),
                drinking_distribution_df=self.lookup_tables["initial_pop_drinking_status_lookup"]

            )
                    
            new_immigrants = immigration_updater.generate_immigration_population(
                population=self.population,
                year=self.year
            )

            self.population = pd.concat([self.population, new_immigrants], ignore_index=True)

        except RuntimeError as e:
            logger.error(f"Failed to update immigration: {e}")
            raise ValueError("An error occurred while updating immigration") from e

    def update_deaths(self):

        """
        Update the population by removing individuals who have died for the current year.
        This method retrieves the death lookup table for the specified year and uses it to update
        the population by marking individuals as not alive based on the death data. Individuals
        who are no longer alive are then removed from the population.
        :raises ValueError: If the death lookup table for the current year is not found.
        :return: None
        """
        # Create an instance of DeathUpdater and update deaths
        death_lookup_table = self.lookup_tables["death_lookup_table"]
        death_lookup_table_year = death_lookup_table[death_lookup_table["Year"] == self.year]
        if death_lookup_table_year.empty:
            logger.error(f"Death lookup table for year {self.year} not found.")
            raise ValueError(f"Death lookup table for year {self.year} not found.")

        death_updater = DeathUpdater(self.population, death_lookup_table_year)
        self.population = death_updater.update_deaths()

        # Remove people who are not alive
        self.population = self.population[self.population["Alive"]]

    def update_drinking_status(self):

        """
        Update the drinking status of the population for the current year.
        This method calculates the drinking year based on the difference between the current year 
        and the initial year, determines the appropriate drinking year group, and retrieves the 
        corresponding drinking status lookup table. The drinking status of the population is then 
        updated using the retrieved lookup table.
        :raises ValueError: If the current year is less than the initial year.
        :raises RuntimeError: If the drinking status lookup table for the determined drinking year 
                      group is not found.
        :return: None
        """

        # Update drinking status based on year
        drinking_year = self.year - self.initial_year

        if drinking_year < 0:
            raise ValueError("Year cannot be less than the initial year.")
        
        # Create drinking_year_group based on drinking_year
        if drinking_year <= 3:
            drinking_year_group = "0-3"
        elif 3 < drinking_year <= 8:
            drinking_year_group = "3-8"
        else:
            drinking_year_group = "8+"

        # retrieve the drinking status lookup table for the current year
        drinking_status_lookup_df = self.lookup_tables.get(drinking_year_group, None)
        if drinking_status_lookup_df is None:
            raise RuntimeError(f"Drinking status lookup for year {self.year} not found.")
        
        drinking_status_updater = DrinkingStatusUpdater(self.population, drinking_status_lookup_df)
        self.population = drinking_status_updater.update_drinking_status()

    def update_age_population(self):

        """
        Increment the age of individuals in the population and cap the maximum age at 100.
        This method updates the "Age" column of the population DataFrame by incrementing 
        each individual's age by 1. If an individual's age exceeds 100 after the increment, 
        it is capped at 100 to ensure no age exceeds this limit.
        """
        
        self.population["Age"] += 1

        self.population.loc[self.population["Age"] > 100, "Age"] = 100

    def simulate_single_year(self):
        """
        Simulates the events and updates for a single year in the population model.
        This function performs the following steps sequentially:
        1. Ages the population by updating their age attributes.
        2. Updates the population with new births.
        3. Updates the population with new immigrants.
        4. Updates the drinking status of individuals in the population.
        5. Updates the population by removing individuals who have died.
        The function logs the time taken for each stage of the simulation, as well as the total time
        taken to simulate the year. It also logs the updated population count at the end of the simulation.
        Attributes:
            self.year (int): The current year being simulated.
            self.population (list): The population data being updated.
            logger (Logger): Logger instance for recording simulation progress and timing.
        """

        logger.info(f"Simulating year: {self.year}")

        # Record start time
        start_time = pd.Timestamp.now()

        # Age the population
        stage_start_time = pd.Timestamp.now()
        self.update_age_population()
        stage_end_time = pd.Timestamp.now()
        logger.info(f"Year {self.year}: Age population updated in {(stage_end_time - stage_start_time).total_seconds():.2f} seconds")

        # Birth update
        stage_start_time = pd.Timestamp.now()
        self.update_births()
        stage_end_time = pd.Timestamp.now()
        logger.info(f"Year {self.year}: Births updated in {(stage_end_time - stage_start_time).total_seconds():.2f} seconds")

        # Immigration update
        stage_start_time = pd.Timestamp.now()
        self.update_immigration()
        stage_end_time = pd.Timestamp.now()
        logger.info(f"Year {self.year}: Immigration updated in {(stage_end_time - stage_start_time).total_seconds():.2f} seconds")

        # Drinking status update
        stage_start_time = pd.Timestamp.now()
        self.update_drinking_status()
        stage_end_time = pd.Timestamp.now()
        logger.info(f"Year {self.year}: Drinking status updated in {(stage_end_time - stage_start_time).total_seconds():.2f} seconds")

        # Death update
        stage_start_time = pd.Timestamp.now()
        self.update_deaths()
        stage_end_time = pd.Timestamp.now()
        logger.info(f"Year {self.year}: Deaths updated in {(stage_end_time - stage_start_time).total_seconds():.2f} seconds")

        # Record end time
        end_time = pd.Timestamp.now()

        # Calculate elapsed time
        elapsed_time = (end_time - start_time).total_seconds()

        # Output the updated population count and elapsed time
        logger.info(f"Year {self.year}: Population count = {len(self.population)}")
        logger.info(f"Year {self.year}: Simulation completed in {elapsed_time:.2f} seconds")
