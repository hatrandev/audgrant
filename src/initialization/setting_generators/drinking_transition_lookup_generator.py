import pandas as pd
from typing import Dict
from src.common.data_reader import ExcelDataReader
from src.common.logger import logger


class DrinkingStatusLookupGenerator:

    def __init__(self, base_path: str, excel_transition_probability_drinking_file_name: str):
        """
        Initialize the DrinkingStatusLookupGenerator with the provided data.

        :param base_path: Base path to the Excel file.
        :param excel_file_name: Name of the Excel file.
        """
        self.base_path = base_path
        self.excel_transition_probability_drinking_file_name = excel_transition_probability_drinking_file_name
        self.data_reader = ExcelDataReader(self.base_path)

        logger.info(f"DrinkingStatusLookupGenerator initialized with base_path: {self.base_path}, "
                    f"excel_transition_probability_drinking_file_name: {self.excel_transition_probability_drinking_file_name}")

    def generate_lookup(self, sheet_name: str) -> Dict[str, pd.DataFrame]:
        """
        Generate the drinking status lookup table.

        :param sheet_name: Name of the sheet to read data from.
        :return: A dictionary with keys "0-3", "3-8", "8+" and corresponding processed DataFrames as values.
        """
        logger.info(f"Reading data from sheet: {sheet_name}")
        data = self.data_reader.read_sheet(self.excel_transition_probability_drinking_file_name, sheet_name=sheet_name)

        data['Composite'] = data['Sex'] + "_" + data['Race']
        data = data.drop(columns=['Sex', 'Race'])
        data = data.rename(columns={'Transition_From': 'Drinking_Stage'})

        wide_data = data.pivot_table(
            index=['Year', 'Age_Group', 'Composite', 'Drinking_Stage'],
            columns='Transition_To',
            values='Rate'
        ).reset_index()

        transition_columns = ['Abs', 'Low', 'Med', 'High', 'Very High']
        wide_data['Drinking_Transition_Probability'] = wide_data[transition_columns].apply(
            lambda row: {col: row[col] / row[transition_columns].sum() for col in transition_columns},
            axis=1
        )

        wide_data = wide_data.drop(columns=transition_columns)

        lookup = {
            "0-3": wide_data[wide_data['Year'] == "0-3"],
            "3-8": wide_data[wide_data['Year'] == "3-8"],
            "8+": wide_data[wide_data['Year'] == "8+"]
        }

        for key in lookup:
            lookup[key] = lookup[key].drop(columns=['Year'])

        return lookup
