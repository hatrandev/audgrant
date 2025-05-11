import pandas as pd
import os
from src.common.logger import logger

class ExcelDataReader:

    def __init__(self, base_path):
        """
        Initialize the ExcelDataReader with the base path to the experiment_setting directory.
        :param base_path: The base directory where the data file is located.
        :param excel_file_name: The name of the Excel file to read.
        """
        self.base_path = base_path
        logger.info(f"ExcelDataReader initialized with base_path: {base_path}")

    def read_sheet(self, excel_file_name, sheet_name):
        """
        Reads the specified sheet from the Excel file.
        :param sheet_name: The name of the sheet to read.
        :return: A pandas DataFrame containing the data from the specified sheet.
        :raises FileNotFoundError: If the file does not exist.
        :raises ValueError: If there is an error reading the sheet.
        """
        file_path = os.path.join(self.base_path, excel_file_name)
        logger.info(f"Attempting to read sheet '{sheet_name}' from file '{file_path}'")

        if not os.path.isfile(file_path):
            logger.error(f"File '{excel_file_name}' does not exist in '{self.base_path}'")
            raise FileNotFoundError(f"The file '{excel_file_name}' does not exist in '{self.base_path}'.")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Successfully read sheet '{sheet_name}' from file '{excel_file_name}'")
            return df
        except ValueError as ve:
            logger.error(f"Sheet '{sheet_name}' does not exist in the file '{excel_file_name}'")
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the file '{excel_file_name}'.") from ve
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading the sheet '{sheet_name}': {e}")
            raise ValueError(f"An unexpected error occurred while reading the sheet '{sheet_name}': {e}") from e

    def validate_columns(self, df, required_columns):
        """
        Validates that the DataFrame contains the required columns.
        :param df: The pandas DataFrame to validate.
        :param required_columns: A list of column names that must be present in the DataFrame.
        :raises ValueError: If any of the required columns are missing.
        """
        logger.info(f"Validating required columns: {required_columns}")
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"The following required columns are missing: {missing_columns}")
        logger.info("All required columns are present.")
