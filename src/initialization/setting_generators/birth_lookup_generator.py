import pandas as pd
from typing import Dict

from src.common.data_reader import ExcelDataReader
from src.common.logger import logger
from src.config.simulation_config import ExperimentConfig
from src.common.constants import ProbabilityRatesColumnNames


class BirthLookupGenerator:

    def __init__(self, base_path: str, excel_file_name: str):
        """
        Initialize the BirthLookupGenerator with the provided data.

        :param base_path: Base path to the Excel file.
        :param excel_file_name: Name of the Excel file.
        """
        self.base_path = base_path
        self.excel_file_name = excel_file_name
        self.data_reader = ExcelDataReader(self.base_path)

        logger.info(f"BirthLookupGenerator initialized with base_path: {self.base_path}, "
                    f"excel_file_name: {self.excel_file_name}")

    def _validate_ratio(self, value: float, value_name: str):
        """
        Validate that a ratio (e.g., Birth_Rate or Male_Ratio) is within the range [0, 1].

        :param value: The ratio value to validate.
        :param value_name: The name of the ratio being validated (e.g., 'Birth_Rate', 'Male_Ratio').
        :raises ValueError: If the ratio is not within the range [0, 1].
        """
        if not (0 <= value <= 1):
            logger.error(f"Invalid {value_name}: {value}. It must be between 0 and 1.")
            raise ValueError(f"Invalid {value_name}: {value}. It must be between 0 and 1.")
        logger.debug(f"Validated {value_name}: {value}")

    def _validate_year(self, year_column: pd.Series):
        """
        Validate that the year column satisfies the required conditions.

        :param year_column: The Year column from the dataframe to validate.
        :raises ValueError: If the conditions are not met.
        """
        min_year = year_column.min()
        max_year = year_column.max()

        if not (min_year - 1 <= ExperimentConfig.INITIAL_YEAR <= max_year):
            logger.error(f"Invalid INITIAL_YEAR: {ExperimentConfig.INITIAL_YEAR}. It must be between "
                         f"{min_year - 1} and {max_year}.")
            raise ValueError(f"Invalid INITIAL_YEAR: {ExperimentConfig.INITIAL_YEAR}. It must be between "
                             f"{min_year - 1} and {max_year}.")

        if not (ExperimentConfig.INITIAL_YEAR <= ExperimentConfig.END_YEAR <= max_year):
            logger.error(f"Invalid END_YEAR: {ExperimentConfig.END_YEAR}. It must be between "
                         f"{ExperimentConfig.INITIAL_YEAR} and {max_year}.")
            raise ValueError(f"Invalid END_YEAR: {ExperimentConfig.END_YEAR}. It must be between "
                             f"{ExperimentConfig.INITIAL_YEAR} and {max_year}.")

        logger.debug(f"Validated Year column with min_year={min_year}, max_year={max_year}, "
                     f"INITIAL_YEAR={ExperimentConfig.INITIAL_YEAR}, END_YEAR={ExperimentConfig.END_YEAR}")

    def generate_lookup_table(self, sheet_name: str, column_name: str) -> Dict[int, float]:
        """
        Generate a lookup table with Year as the key and the specified column as the value.

        :param sheet_name: The name of the sheet to read from the Excel file.
        :param column_name: The name of the column to use as the value in the lookup table.
        :return: Dictionary representing the lookup table.
        """
        logger.info(f"Reading data from sheet: {sheet_name}")
        data = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        lookup_table = {}

        if "Year" not in data.columns or column_name not in data.columns:
            logger.error(f"The dataframe must contain 'Year' and '{column_name}' columns.")
            raise ValueError(f"The dataframe must contain 'Year' and '{column_name}' columns.")
        
        self._validate_year(data["Year"])

        data = data[(data["Year"] >= ExperimentConfig.INITIAL_YEAR + 1) & (data["Year"] <= ExperimentConfig.END_YEAR)]

        for _, row in data.iterrows():
            year = row["Year"]
            value = row[column_name]
            
            self._validate_ratio(value, column_name)

            if pd.isna(year) or pd.isna(value):
                logger.error(f"Each row must contain non-null 'Year' and '{column_name}' values.")
                raise ValueError(f"Each row must contain non-null 'Year' and '{column_name}' values.")

            if ExperimentConfig.INITIAL_YEAR <= year <= ExperimentConfig.END_YEAR:
                lookup_table[year] = value
                logger.debug(f"Added to lookup_table: Year={year}, {column_name}={value}")

        if not lookup_table:
            logger.error(f"Generated lookup table for {column_name} is empty.")
            raise ValueError(f"Generated lookup table for {column_name} is empty.")

        logger.info(f"Lookup table generation for {column_name} completed.")
        return lookup_table
    
    def generate_lookup_race_table(self, sheet_name):
        
        """
        Generate a lookup table for race data under 5 years old.

        :param sheet_name: The name of the sheet containing Race data.
        :return: A dictionary with the structure:
             {year: {gender: {race: proportion}}}, where proportion is the
             fraction of the population of a specific race for the given year and gender.
        """
        
        logger.info(f"Processing race data for 'Under 5 years' from sheet: {sheet_name}")
        try:
            initial_population_race_df = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}': {e}")
            raise ValueError(f"Error reading sheet '{sheet_name}': {e}")

        # Filter data for 'Under 5 years' and valid years
        filtered_df = initial_population_race_df[
            (initial_population_race_df[ProbabilityRatesColumnNames.AGE_GROUP_COLUMN] == "Under 5 years") &
            (initial_population_race_df[ProbabilityRatesColumnNames.YEAR_COLUMN] > ExperimentConfig.INITIAL_YEAR) &
            (initial_population_race_df[ProbabilityRatesColumnNames.YEAR_COLUMN] <= ExperimentConfig.END_YEAR)
        ]

        if (ProbabilityRatesColumnNames.TOTAL_POPULATION_COLUMN not in filtered_df or
                ProbabilityRatesColumnNames.POPULATION_COUNT_COLUMN not in filtered_df):
            logger.error("Required columns are missing in the race data sheet.")
            raise ValueError("Required columns are missing in the race data sheet.")
        
        if filtered_df.empty:
            logger.error("Filtered dataframe for 'Under 5 years' is empty.")
            raise ValueError("Filtered dataframe for 'Under 5 years' is empty.")
            
        grouped = filtered_df.groupby(
            [ProbabilityRatesColumnNames.YEAR_COLUMN, ProbabilityRatesColumnNames.SEX_COLUMN]
        )

        race_ratio_lookup = {}

        for (year, gender), group in grouped:
            # Calculate total population for normalization
            total_population = group[ProbabilityRatesColumnNames.POPULATION_COUNT_COLUMN].sum()
            if total_population == 0:
                logger.error(f"Total population for year {year}, gender {gender} is zero.")
                raise ValueError(f"Total population for year {year}, gender {gender} must not be zero.")

            # Initialize nested dictionary for the year and gender
            if year not in race_ratio_lookup:
                race_ratio_lookup[year] = {}
            race_ratio_lookup[year][gender] = {}

            # Populate race proportions
            for _, row in group.iterrows():
                race = row[ProbabilityRatesColumnNames.RACE_COLUMN]
                population_count = row[ProbabilityRatesColumnNames.POPULATION_COUNT_COLUMN]
                race_ratio_lookup[year][gender][race] = population_count / total_population

        logger.info(f"Processed race data for 'Under 5 years': {len(race_ratio_lookup)} years found.")
        return race_ratio_lookup

    def generate_all_lookup_tables(self, birth_rate_sheet: str, male_ratio_sheet: str, race_sheet_name: str) -> Dict[str, Dict[int, float]]:
        """
        Generate all Birth_Rate, Male_Ratio, and Race lookup tables.

        :param birth_rate_sheet: The name of the sheet containing Birth_Rate data.
        :param male_ratio_sheet: The name of the sheet containing Male_Ratio data.
        :param race_sheet_name: The name of the sheet containing Race data.
        :return: A dictionary containing all lookup tables.
        """
        birth_rate_table = self.generate_lookup_table(birth_rate_sheet, "Birth_Rate")
        male_ratio_table = self.generate_lookup_table(male_ratio_sheet, "Male_Ratio")
        race_lookup_under_5_table = self.generate_lookup_race_table(race_sheet_name)

        return {
            "birth_rate_table": birth_rate_table,
            "birth_male_ratio_table": male_ratio_table,
            "birth_race_lookup_under_5_table": race_lookup_under_5_table
        }
