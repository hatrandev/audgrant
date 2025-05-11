from typing import Dict
from src.config.simulation_config import ExperimentConfig
from src.common.constants import ProbabilityRatesColumnNames
from src.common.data_reader import ExcelDataReader
from src.common.logger import logger

class ImmigrationLookupGenerator:

    def __init__(self, base_path: str, excel_file_name: str):

        """
        Initialize the ImmigrationLookupGenerator with the base path and Excel file name.

        :param base_path: The base path to the directory containing the Excel file.
        :param excel_file_name: The name of the Excel file containing the data.
        """
        self.base_path = base_path
        self.excel_file_name = excel_file_name
        self.data_reader = ExcelDataReader(self.base_path)
        logger.info(f"ImmigrationLookupGenerator initialized with base_path: {self.base_path}, "
                    f"excel_file_name: {self.excel_file_name}")

    def generate_lookup(self, sheet_name: str, ratio_column: str, key_column: str) -> Dict:
        """
        Generate a lookup table from the specified sheet in the Excel file.

        :param sheet_name: The name of the sheet to read data from.
        :param ratio_column: The column name containing the ratio values.
        :param key_column: The column name to use as the key for the lookup.
        :return: A nested dictionary representing the lookup table.
        """
        logger.info(f"Generating lookup for sheet: {sheet_name}, ratio_column: {ratio_column}, key_column: {key_column}")
        dataframe = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        
        # Filter rows based on the year range
        dataframe = dataframe[(dataframe[ProbabilityRatesColumnNames.YEAR_COLUMN] > ExperimentConfig.INITIAL_YEAR) & 
                              (dataframe[ProbabilityRatesColumnNames.YEAR_COLUMN] <= ExperimentConfig.END_YEAR)]

        lookup = {}
        for _, row in dataframe.iterrows():
            year = row[ProbabilityRatesColumnNames.YEAR_COLUMN]
            key = row[key_column]
            ratio = row[ratio_column]
            if year not in lookup:
                lookup[year] = {}
            if key_column not in lookup[year]:
                lookup[year][key_column] = {}
            lookup[year][key_column][key] = ratio
        logger.info(f"Lookup generated for sheet: {sheet_name}")
        return lookup

    def generate_age_lookup(self, sheet_name: str):
        """
        Generate a lookup table for age-related data.

        :param sheet_name: The name of the sheet containing age-related data.
        """
        logger.info(f"Generating age lookup from sheet: {sheet_name}")
        self.age_lookup = self.generate_lookup(
            sheet_name,
            ProbabilityRatesColumnNames.AGE_RATIO_COLUMN,
            ProbabilityRatesColumnNames.AGE_COLUMN
        )
        logger.info("Age lookup generation completed.")
        return self.age_lookup

    def generate_sex_lookup(self, sheet_name: str):
        """
        Generate a lookup table for sex-related data.

        :param sheet_name: The name of the sheet containing sex-related data.
        """
        logger.info(f"Generating sex lookup from sheet: {sheet_name}")
        self.sex_lookup = self.generate_lookup(
            sheet_name,
            ProbabilityRatesColumnNames.MALE_RATIO_COLUMN,
            ProbabilityRatesColumnNames.AGE_COLUMN
        )
        logger.info("Sex lookup generation completed.")
        return self.sex_lookup

    def generate_race_lookup(self, sheet_name: str):
        """
        Generate a normalized lookup table for race-related data.

        :param sheet_name: The name of the sheet containing race-related data.
        """
        logger.info(f"Generating race lookup from sheet: {sheet_name}")
        dataframe = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        normalized_data = {}

        dataframe = dataframe[(dataframe[ProbabilityRatesColumnNames.YEAR_COLUMN] > ExperimentConfig.INITIAL_YEAR) & 
                              (dataframe[ProbabilityRatesColumnNames.YEAR_COLUMN] <= ExperimentConfig.END_YEAR)]

        for _, row in dataframe.iterrows():
            year = row[ProbabilityRatesColumnNames.YEAR_COLUMN]
            sex = row[ProbabilityRatesColumnNames.SEX_COLUMN]
            age_group = row[ProbabilityRatesColumnNames.AGE_GROUP_COLUMN]
            race = row[ProbabilityRatesColumnNames.RACE_COLUMN]
            ratio = row[ProbabilityRatesColumnNames.RACE_PROPORTION_COLUMN]

            if year not in normalized_data:
                normalized_data[year] = {}
            if sex not in normalized_data[year]:
                normalized_data[year][sex] = {}
            if age_group not in normalized_data[year][sex]:
                normalized_data[year][sex][age_group] = {}
            if race not in normalized_data[year][sex][age_group]:
                normalized_data[year][sex][age_group][race] = 0

            normalized_data[year][sex][age_group][race] += ratio

        for year, sexes in normalized_data.items():
            for sex, age_groups in sexes.items():
                for age_group, races in age_groups.items():
                    total_ratio = sum(races.values())
                    if total_ratio > 0:
                        for race in races:
                            races[race] /= total_ratio

        self.race_lookup = normalized_data
        logger.info("Race lookup generation completed.")
        return self.race_lookup

    def generate_immigration_rate_lookup(self, sheet_name: str) -> Dict:
        """
        Generate a lookup table for immigration rates.

        :param sheet_name: The name of the sheet containing immigration rate data.
        :return: A dictionary with years as keys and immigration rates as values.
        """
        logger.info(f"Generating immigration rate lookup from sheet: {sheet_name}")
        dataframe = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        immigration_rate_lookup = {}

        for _, row in dataframe.iterrows():
            year = row[ProbabilityRatesColumnNames.YEAR_COLUMN]
            immigration_rate = row[ProbabilityRatesColumnNames.IMMIGRATION_RATE_COLUMN]
            if not (0 <= immigration_rate <= 1):
                logger.error(f"Immigration rate {immigration_rate} for year {year} is out of bounds (0-1).")
                raise ValueError(f"Immigration rate {immigration_rate} for year {year} is out of bounds (0-1).")
            immigration_rate_lookup[year] = immigration_rate

        logger.info("Immigration rate lookup generation completed.")
        return immigration_rate_lookup

    def validate_lookup(self, lookup: Dict, initial_year: int, end_year: int, sum_check: bool = False):
        """
        Validate a lookup table based on year range and ratio constraints.

        :param lookup: The lookup table to validate.
        :param initial_year: The initial year for validation.
        :param end_year: The end year for validation.
        :param sum_check: Whether to check if the sum of ratios by year is close to 1.
        :return: True if the lookup is valid, False otherwise.
        """
        for year, data in lookup.items():
            if not (initial_year <= year <= end_year):
                logger.error(f"Year {year} is out of range ({initial_year}-{end_year}).")
                return False
            for key, ratios in data.items():
                for sub_key, ratio in ratios.items():
                    try:
                        if not (0 <=ratio <= 1):
                            logger.error(f"Ratio {rt} for year {year}, key {key}, sub_key {sub_key} is out of bounds (0-1).")
                            return False
                    except TypeError:
                        for _, rt in ratio.items():
                            if not (0 <= rt <= 1):
                                logger.error(f"Ratio {rt} for year {year}, key {key}, sub_key {sub_key} is out of bounds (0-1).")
                                return False
            if sum_check:
                total_ratio = sum(ratio for key in data.values() for ratio in key.values())
                if not (0.99 <= total_ratio <= 1.01):
                    logger.error(f"Total ratio for year {year} is not close to 1: {total_ratio}.")
                    return False
        logger.info("Lookup validation passed.")
        return True

    def generate_all_lookups(self, age_sheet: str, sex_sheet: str, race_sheet: str, immigration_rate_sheet: str):
        """
        Generate all lookup tables (age, sex, race, and immigration rate) and return them as a dictionary.

        :param age_sheet: The name of the sheet containing age-related data.
        :param sex_sheet: The name of the sheet containing sex-related data.
        :param race_sheet: The name of the sheet containing race-related data.
        :param immigration_rate_sheet: The name of the sheet containing immigration rate data.
        :return: A dictionary containing all generated lookup tables.
        """
        logger.info("Starting generation of all lookups.")
        age_lookup = self.generate_age_lookup(age_sheet)
        sex_lookup = self.generate_sex_lookup(sex_sheet)
        race_lookup = self.generate_race_lookup(race_sheet)
        immigration_rate_lookup = self.generate_immigration_rate_lookup(immigration_rate_sheet)

        initial_year = ExperimentConfig.INITIAL_YEAR
        end_year = ExperimentConfig.END_YEAR

        if not self.validate_lookup(age_lookup, initial_year, end_year, sum_check=True):
            raise ValueError("Age lookup validation failed.")
        if not self.validate_lookup(sex_lookup, initial_year, end_year, sum_check=False):
            raise ValueError("Sex lookup validation failed.")
        if not self.validate_lookup(race_lookup, initial_year, end_year, sum_check=False):
            raise ValueError("Race lookup validation failed.")

        return {
            "immigration_age_lookup": age_lookup,
            "immigration_sex_lookup": sex_lookup,
            "immigration_race_lookup": race_lookup,
            "immigration_rate_lookup": immigration_rate_lookup
        }

if __name__ == "__main__":
    base_path = "src/experiment_setting/data"
    excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
    birth_rate_sheet = "Age_Ratio_All_Years"
    male_ratio_sheet = "Sex_Ratio_All_Years"
    race_sheet_name = "Race_Sex_Age"
    immigration_rate_sheet = "Immigration"

    generator = ImmigrationLookupGenerator(base_path, excel_file_name)
    lookups = generator.generate_all_lookups(birth_rate_sheet, male_ratio_sheet, race_sheet_name, immigration_rate_sheet)

    print(lookups)  