from src.common.data_reader import ExcelDataReader
from src.config.simulation_config import ExperimentConfig
from src.common.constants import ProbabilityRatesColumnNames
from src.common.common import Common_RNG
from src.common.logger import logger
import pandas as pd
import random
import numpy as np

class InitialPopulationLookupGenerator:

    def __init__(self, base_path, excel_file_name, excel_drinking_file_name):

        logger.info("Initializing InitialPopulationLookupGenerator")
        self.base_path = base_path
        self.excel_file_name = excel_file_name
        self.excel_drinking_file_name = excel_drinking_file_name
        self.data_reader = ExcelDataReader(self.base_path)

    def process_initial_population_race_data(self, sheet_name):

        """
        Process race data from the specified sheet and generate a lookup table.
        This function reads race-related data from an Excel sheet, filters it for the initial year,
        calculates race proportions, and organizes the data into a nested dictionary lookup table
        based on age group and sex.
        :param sheet_name: The name of the sheet to read data from.
        :return: A nested dictionary where the keys are tuples of (age group, sex) and the values
                 are dictionaries mapping race to its proportion.
        :raises ValueError: If the sheet cannot be read, required columns are missing, or any other
                            issue occurs during processing.
        """

        logger.info(f"Processing race data from sheet: {sheet_name}")
        try:
            initial_population_race_df = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}': {e}")
            raise ValueError(f"Error reading sheet '{sheet_name}': {e}")

        initial_population_race_df = initial_population_race_df[
            initial_population_race_df[ProbabilityRatesColumnNames.YEAR_COLUMN] == ExperimentConfig.INITIAL_YEAR
        ]
        if (ProbabilityRatesColumnNames.TOTAL_POPULATION_COLUMN not in initial_population_race_df or
                ProbabilityRatesColumnNames.POPULATION_COUNT_COLUMN not in initial_population_race_df):
            logger.error("Required columns are missing in the race data sheet.")
            raise ValueError("Required columns are missing in the race data sheet.")

        initial_population_race_df[ProbabilityRatesColumnNames.RACE_PROPORTION_COLUMN] = (
            initial_population_race_df[ProbabilityRatesColumnNames.POPULATION_COUNT_COLUMN] /
            initial_population_race_df[ProbabilityRatesColumnNames.TOTAL_POPULATION_COLUMN]
        )
        race_ratio_lookup = {}
        for _, row in initial_population_race_df.iterrows():
            key = (row[ProbabilityRatesColumnNames.AGE_GROUP_COLUMN], row[ProbabilityRatesColumnNames.SEX_COLUMN])
            race = row[ProbabilityRatesColumnNames.RACE_COLUMN]
            prob = row[ProbabilityRatesColumnNames.RACE_PROPORTION_COLUMN]
            race_ratio_lookup.setdefault(key, {})[race] = prob

        logger.info(f"Processed race data: {len(race_ratio_lookup)} unique age-sex groups found.")
        return race_ratio_lookup
    
    def process_initial_population_drinking_data(self, sheet_name):

        """
        Process drinking data from the specified sheet and generate a lookup table.
        This function reads drinking-related data from an Excel sheet, filters it for the initial year,
        pivots the data to a wide format, normalizes the drinking risk proportions, and organizes the
        data into a structured format for further use.
        :param sheet_name: The name of the sheet to read data from.
        :return: A DataFrame containing drinking status proportions for each combination of race, sex,
             and age group, along with a composite key combining sex and race.
        :raises ValueError: If the sheet cannot be read, required columns are missing, or any other
                    issue occurs during processing.
        """

        logger.info(f"Processing drinking data from sheet: {sheet_name}")
        try:
            initial_population_drinking_df = self.data_reader.read_sheet(self.excel_drinking_file_name, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}': {e}")
            raise ValueError(f"Error reading sheet '{sheet_name}': {e}")

        initial_population_drinking_df = initial_population_drinking_df[
            initial_population_drinking_df[ProbabilityRatesColumnNames.YEAR_COLUMN] == ExperimentConfig.INITIAL_YEAR
        ]

        drinking_status_df = initial_population_drinking_df.pivot_table(
            index=["Race", "Sex", "Age_Group"],
            columns="Drinking_Stage",
            values="Rate",
            aggfunc="sum"
        ).fillna(0)

        drinking_status_df = drinking_status_df.reset_index()

        unique_race_sex_combinations = initial_population_drinking_df[["Race", "Sex"]].drop_duplicates()
        new_rows = []
        for _, row in unique_race_sex_combinations.iterrows():
            new_rows.append({
            "Race": row["Race"],
            "Sex": row["Sex"],
            "Age_Group": "0-17",
            "Abs": 1,
            "High": 0,
            "Low": 0,
            "Med": 0,
            "Very High": 0
            })
        drinking_status_df = pd.concat([drinking_status_df, pd.DataFrame(new_rows)], ignore_index=True)

        drinking_status_df.loc[
            (drinking_status_df == 0).all(axis=1), "Abs"
        ] = 1

        risk_columns = ["Abs", "High", "Low", "Med", "Very High"]
        drinking_status_df[risk_columns] = drinking_status_df[risk_columns].div(
            drinking_status_df[risk_columns].sum(axis=1), axis=0
        ).fillna(0)

        drinking_status_df["Drinking_Status"] = drinking_status_df[risk_columns].apply(
            lambda row: {col: row[col] for col in risk_columns}, axis=1
        )

        drinking_status_df = drinking_status_df[["Race", "Sex", "Age_Group", "Drinking_Status"]]

        drinking_status_df['Composite'] = drinking_status_df.apply(
            lambda row: f"{row['Sex']}_{row['Race']}", axis=1
        )

        drinking_status_df.drop(columns=["Race", "Sex"], inplace=True)

        logger.info(f"Processed drinking data: {len(drinking_status_df)} unique groups found.")

        drinking_status_df = drinking_status_df.reset_index(drop=True)

        return drinking_status_df
    
    def process_initial_population_age_data(self, sheet_name):
        
        """
        Process age data from the specified sheet and generate an age ratio lookup table.
        This function reads age-related data from an Excel sheet, filters it for the initial year,
        and organizes the data into a dictionary where age groups are mapped to their respective ratios.
        :param sheet_name: The name of the sheet to read data from.
        :return: A dictionary where the keys are age groups (as integers) and the values are their corresponding ratios.
        :raises ValueError: If no data is found for the specified initial year in the sheet.
        """

        logger.info(f"Processing age data from sheet: {sheet_name}")
        initial_population_age_df = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        initial_population_age_df = initial_population_age_df[
            initial_population_age_df[ProbabilityRatesColumnNames.YEAR_COLUMN] == ExperimentConfig.INITIAL_YEAR
        ]

        if len(initial_population_age_df) == 0:
            logger.error(f"No data found for the year {ExperimentConfig.INITIAL_YEAR} in the sheet '{sheet_name}'.")
            raise ValueError(f"No data found for the year {ExperimentConfig.INITIAL_YEAR} in the sheet '{sheet_name}'.")

        age_ratio_lookup = {}
        for _, row in initial_population_age_df.iterrows():
            age_group = int(row[ProbabilityRatesColumnNames.AGE_COLUMN])
            ratio = row[ProbabilityRatesColumnNames.AGE_RATIO_COLUMN]
            age_ratio_lookup[age_group] = ratio

        logger.info(f"Processed age data: {len(age_ratio_lookup)} unique age groups found.")
        return age_ratio_lookup
    
    def process_initial_population_sex_data(self, sheet_name):

        """
        Process sex data from the specified sheet and generate a sex ratio lookup table.
        This function reads sex-related data from an Excel sheet, extracts the male ratio for each age group,
        and organizes the data into a dictionary where age groups are mapped to their respective male ratios.
        :param sheet_name: The name of the sheet to read data from.
        :return: A dictionary where the keys are age groups (as defined in the sheet) and the values are their corresponding male ratios.
        :raises ValueError: If there is an error reading the specified sheet.
        """

        logger.info(f"Processing sex data from sheet: {sheet_name}")
        try:
            initial_population_sex_df = self.data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}': {e}")
            raise ValueError(f"Error reading sheet '{sheet_name}': {e}")

        sex_ratio_lookup = {}
        for _, row in initial_population_sex_df.iterrows():
            age_group = row[ProbabilityRatesColumnNames.AGE_COLUMN]
            male_ratio = row[ProbabilityRatesColumnNames.MALE_RATIO_COLUMN]
            sex_ratio_lookup[age_group] = male_ratio

        logger.info(f"Processed sex data: {len(sex_ratio_lookup)} unique age groups found.")
        return sex_ratio_lookup
    
    def generate_initial_population_lookups(self, 
                                            age_sheet_name, 
                                            sex_sheet_name, 
                                            race_sheet_name, 
                                            drinking_prevalence_sheet_name):
        
        """
        Generate initial population lookup tables based on demographic and drinking prevalence data.
        This function processes data from specified Excel sheets to create lookup tables for race, age, sex, 
        and drinking status distributions. These lookup tables are used to initialize population data 
        for further modeling or analysis.
        :param age_sheet_name: The name of the Excel sheet containing age distribution data.
        :param sex_sheet_name: The name of the Excel sheet containing sex distribution data.
        :param race_sheet_name: The name of the Excel sheet containing race distribution data.
        :param drinking_prevalence_sheet_name: The name of the Excel sheet containing drinking prevalence data.
        :return: A dictionary containing the generated lookup tables with the following keys:
                - "initial_pop_race_lookup": Lookup table for race distribution.
                - "initial_pop_age_lookup": Lookup table for age distribution.
                - "initial_pop_sex_lookup": Lookup table for sex distribution.
                - "initial_pop_drinking_status_lookup": Lookup table for drinking status distribution.
        :raises ValueError: If there is an error processing any of the input data sheets.
        """

        logger.info("Generating initial population lookup tables.")
        try:
            race_lookup = self.process_initial_population_race_data(race_sheet_name)
            age_lookup = self.process_initial_population_age_data(age_sheet_name)
            sex_lookup = self.process_initial_population_sex_data(sex_sheet_name)
            drinking_status_lookup = self.process_initial_population_drinking_data(drinking_prevalence_sheet_name)
        except Exception as e:
            logger.error(f"Error generating initial population lookup tables: {e}")
            raise ValueError(f"Error generating initial population lookup tables: {e}")

        initial_population_lookups = {
            "initial_pop_race_lookup": race_lookup,
            "initial_pop_age_lookup": age_lookup,
            "initial_pop_sex_lookup": sex_lookup,
            "initial_pop_drinking_status_lookup": drinking_status_lookup
        }
        logger.info("Initial population lookup tables generated successfully.")
        return initial_population_lookups
    

if __name__ == "__main__":
    base_path = "test/data/input_data"
    excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
    
    age_sheet_name = "Initial_Population"
    sex_sheet_name = "Sex_Average"
    race_sheet_name = "Race_Sex_Age"
    drinking_prevalence_sheet_name = "Drinking_Prevalence"

    generator = InitialPopulationLookupGenerator(base_path, excel_file_name)
    
    try:
        race_data = generator.process_initial_population_race_data(race_sheet_name)
        print("Race Data:", race_data)
    except Exception as e:
        print(f"Error processing race data: {e}")

    try:
        age_data = generator.process_initial_population_age_data(age_sheet_name)
        print("Age Data:", age_data)
    except Exception as e:
        print(f"Error processing age data: {e}")

    try:
        sex_data = generator.process_initial_population_sex_data(sex_sheet_name)
        print("Sex Data:", sex_data)
    except Exception as e:
        print(f"Error processing sex data: {e}")

    try:
        drinking_data = generator.process_initial_population_drinking_data(drinking_prevalence_sheet_name)
        print("Drinking Data:", drinking_data)
    except Exception as e:
        print(f"Error processing drinking data: {e}")
        