from src.common.logger import logger
from src.initialization.initial_population_generator import PopulationInitializer
from src.initialization.lookup_tables_generator import LookupTablesGenerator
import time

class Initializer:
    def __init__(self, 
                 base_path: str, 
                 excel_file_name: str,
                 excel_transition_probability_drinking_file_name: str,
                 excel_drinking_file_name: str, 
                 seed=None):
        """
        Initialize the SimulationInitializer class.

        :param base_path: The directory path where lookup tables will be generated.
        :param excel_file_name: The name of the Excel file containing input data.
        :param age_distribution_dict: Dictionary with age groups and their proportions.
        :param sex_distribution_dict: Dictionary with age groups and gender ratios.
        :param race_distribution_dict: Dictionary with (age group, gender) and race proportions.
        :param seed: Optional random seed for reproducibility.
        """
        self.lookup_tables_generator = LookupTablesGenerator(base_path, 
                                                             excel_file_name, 
                                                             excel_transition_probability_drinking_file_name, 
                                                             excel_drinking_file_name)
        self.seed = seed


    def initialize_population(self, age_distribution_dict, sex_distribution_dict, race_distribution_dict):
        
        """
        Initialize the population using the PopulationInitializer class.

        :return: The initial population.
        """

        logger.info("Initializing population...")
        self.population_initializer = PopulationInitializer(age_distribution_dict, 
                                                            sex_distribution_dict, 
                                                            race_distribution_dict,
                                                            self.seed)
        initial_population = self.population_initializer.generate_initial_population()
        logger.info("Population initialization complete.")
        return initial_population
    
    def initialize_simulation(self, 
                              birth_rate_sheet: str, 
                              birth_male_ratio_sheet: str, 
                              birth_race_sheet_name: str, 
                              death_sheet_name: str, 
                              death_rate_column_name: str, 
                              immigration_age_sheet: str, 
                              immigration_sex_sheet: str, 
                              immigration_race_sheet: str, 
                              immigration_rate_sheet: str,
                              drinking_transition_sheet_name: str, 
                              initial_population_age_sheet: str, 
                              initial_population_sex_sheet: str, 
                              initial_population_race_sheet: str,
                              drinking_prevalence_sheet_name: str):
        """
        Initialize the simulation by generating lookup tables and the initial population.

        :param birth_rate_sheet: Name of the sheet containing birth rate data.
        :param birth_male_ratio_sheet: Name of the sheet containing birth male ratio data.
        :param birth_race_sheet_name: Name of the sheet containing birth race data.
        :param death_sheet_name: Name of the sheet containing death rate data.
        :param death_rate_column_name: Name of the column containing death rate data.
        :param immigration_age_sheet: Name of the sheet containing immigration age data.
        :param immigration_sex_sheet: Name of the sheet containing immigration sex data.
        :param immigration_race_sheet: Name of the sheet containing immigration race data.
        :param immigration_rate_sheet: Name of the sheet containing immigration rate data.
        :param initial_population_age_sheet: Name of the sheet containing initial population age data.
        :param initial_population_sex_sheet: Name of the sheet containing initial population sex data.
        :param initial_population_race_sheet: Name of the sheet containing initial population race data.
        :return: A tuple containing the lookup tables and the initial population.
        """
        logger.info("Initializing simulation...")

        start_time = time.time()
        lookup_tables = self.lookup_tables_generator.create_lookup_tables(
            birth_rate_sheet=birth_rate_sheet,
            birth_male_ratio_sheet=birth_male_ratio_sheet,
            birth_race_sheet_name=birth_race_sheet_name,
            death_sheet_name=death_sheet_name,
            death_rate_column_name=death_rate_column_name,
            immigration_age_sheet=immigration_age_sheet,
            immigration_sex_sheet=immigration_sex_sheet,
            immigration_race_sheet=immigration_race_sheet,
            immigration_rate_sheet=immigration_rate_sheet,
            drinking_transition_sheet_name=drinking_transition_sheet_name,
            initial_population_age_sheet=initial_population_age_sheet,
            initial_population_sex_sheet=initial_population_sex_sheet,
            initial_population_race_sheet=initial_population_race_sheet,
            drinking_prevalence_sheet_name=drinking_prevalence_sheet_name
        )
        end_time = time.time()
        logger.info(f"Lookup tables generation took {end_time - start_time:.2f} seconds.")

        start_time = time.time()
        population_initializer = PopulationInitializer(lookup_tables['initial_pop_age_lookup'],
                                   lookup_tables['initial_pop_sex_lookup'], 
                                   lookup_tables['initial_pop_race_lookup'],
                                   lookup_tables['initial_pop_drinking_status_lookup'],)

        initial_population = population_initializer.generate_initial_population()
        end_time = time.time()
        logger.info(f"Population initialization took {end_time - start_time:.2f} seconds.")

        logger.info("Simulation initialization complete.")
        return lookup_tables, initial_population
