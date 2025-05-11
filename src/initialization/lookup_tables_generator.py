from src.initialization.setting_generators.birth_lookup_generator import BirthLookupGenerator
from src.initialization.setting_generators.death_lookup_generator import DeathLookupGenerator
from src.initialization.setting_generators.immigration_lookup_generator import ImmigrationLookupGenerator
from src.initialization.setting_generators.initial_population_lookup_generator import InitialPopulationLookupGenerator
from src.initialization.setting_generators.drinking_transition_lookup_generator import DrinkingStatusLookupGenerator
from src.common.logger import logger

class LookupTablesGenerator:

    def __init__(self, 
                 base_path: str, 
                 excel_file_name: str, 
                 excel_transition_probability_drinking_file_name: str, 
                 excel_drinking_file_name: str):
        """
        Initialize the LookupTablesGenerator instance with the required parameters.

        :param base_path: The directory path where lookup tables will be generated.
        :param excel_file_name: The name of the Excel file containing input data.
        """
        self.base_path = base_path
        self.excel_file_name = excel_file_name
        self.excel_transition_probability_drinking_file_name = excel_transition_probability_drinking_file_name
        self.excel_drinking_file_name = excel_drinking_file_name
        logger.info(
            "Initialized LookupTablesGenerator with base_path: %s, excel_file_name: %s",
            base_path, excel_file_name
        )

    def _initialize_generators(self):
        """
        Initialize all lookup table generators.

        :return: A dictionary of initialized generators.
        """
        logger.info("Initializing all lookup generators.")
        return {
            "birth": BirthLookupGenerator(self.base_path, self.excel_file_name),
            "death": DeathLookupGenerator(self.base_path, self.excel_file_name),
            "immigration": ImmigrationLookupGenerator(self.base_path, self.excel_file_name),
            "drinking_transition": DrinkingStatusLookupGenerator(self.base_path, self.excel_transition_probability_drinking_file_name),
            "initial_population": InitialPopulationLookupGenerator(self.base_path, self.excel_file_name, self.excel_drinking_file_name)
        }

    def _log_and_generate(self, generator_name: str, generator_method, **kwargs):
        """
        Log the start and end of a lookup table generation process.

        :param generator_name: The name of the generator.
        :param generator_method: The method to call for generating the lookup table.
        :param kwargs: Additional arguments to pass to the generator method.
        :return: The generated lookup table.
        """
        logger.info(f"Generating {generator_name} lookup tables.")
        try:
            result = generator_method(**kwargs)
            logger.info(f"Successfully generated {generator_name} lookup tables.")
            return result
        except Exception as e:
            logger.error(f"Failed to generate {generator_name} lookup tables: {e}")
            raise RuntimeError(f"Error generating {generator_name} lookup tables.") from e

    def create_lookup_tables(self, 
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
                             drinking_prevalence_sheet_name: str) -> dict:
        
        """
        Generate and return lookup tables using the associated generators.

        :param birth_rate_sheet: Sheet name for birth rate data.
        :param birth_male_ratio_sheet: Sheet name for male ratio data.
        :param birth_race_sheet_name: Sheet name for race data.
        :param death_sheet_name: Sheet name for death data.
        :param death_rate_column_name: Column name for death rate data.
        :param immigration_age_sheet: Sheet name for immigration age data.
        :param immigration_sex_sheet: Sheet name for immigration sex data.
        :param immigration_race_sheet: Sheet name for immigration race data.
        :param immigration_rate_sheet: Sheet name for immigration rate data.
        :param initial_population_age_sheet: Sheet name for initial population age data.
        :param initial_population_sex_sheet: Sheet name for initial population sex data.
        :param initial_population_race_sheet: Sheet name for initial population race data.
        :return: A dictionary containing the generated lookup tables.
        """
        logger.info("Starting to create lookup tables.")

        # Initialize generators
        generators = self._initialize_generators()

        # Generate lookup tables
        birth_lookup_tables = self._log_and_generate(
            "birth",
            generators["birth"].generate_all_lookup_tables,
            birth_rate_sheet=birth_rate_sheet,
            male_ratio_sheet=birth_male_ratio_sheet,
            race_sheet_name=birth_race_sheet_name
        )

        death_lookup_table = self._log_and_generate(
            "death",
            generators["death"].load_lookup_table,
            sheet_name=death_sheet_name,
            column_name=death_rate_column_name
        )

        immigration_lookup_tables = self._log_and_generate(
            "immigration",
            generators["immigration"].generate_all_lookups,
            age_sheet=immigration_age_sheet,
            sex_sheet=immigration_sex_sheet,
            race_sheet=immigration_race_sheet,
            immigration_rate_sheet = immigration_rate_sheet
        )

        drinking_transition_lookup_tables = self._log_and_generate(
            "drinking_transition",
            generators["drinking_transition"].generate_lookup,
            sheet_name=drinking_transition_sheet_name
        )

        initial_population_lookups = self._log_and_generate(
            "initial_population",
            generators["initial_population"].generate_initial_population_lookups,
            age_sheet_name=initial_population_age_sheet,
            sex_sheet_name=initial_population_sex_sheet,
            race_sheet_name=initial_population_race_sheet,
            drinking_prevalence_sheet_name=drinking_prevalence_sheet_name
        )

        lookup_tables = {
            **birth_lookup_tables,
            "death_lookup_table": death_lookup_table,
            **immigration_lookup_tables,
            **initial_population_lookups,
            **drinking_transition_lookup_tables,
        }

        logger.info("Lookup tables generated successfully.")
        return lookup_tables
    