import pandas as pd

from src.common.data_reader import ExcelDataReader
from src.common.logger import logger
from src.config.simulation_config import ExperimentConfig

class DeathLookupGenerator:

    def __init__(self, base_path: str, excel_file_name: str):
        """
        Initialize the BirthLookupTable by loading data from an Excel file.

        :param base_path: Base path to the Excel file.
        :param excel_file_name: Name of the Excel file.
        :param sheet_name: Name of the sheet to read from the Excel file.
        :param column_name: Name of the column to use as the birth rate.
        """
        self.base_path = base_path
        self.excel_file_name = excel_file_name
        self.lookup_table = {}

    def load_lookup_table(self, sheet_name: str, column_name: str) -> pd.DataFrame:
        """
        Load the lookup table from the Excel file and convert it to a DataFrame with the desired format.
        """
        data_reader = ExcelDataReader(self.base_path)
        data = data_reader.read_sheet(self.excel_file_name, sheet_name=sheet_name)

        required_columns = {"Year", "Sex", "Race", "Age", column_name}
        if not required_columns.issubset(data.columns):
            logger.error(f"The dataframe must contain the following columns: {required_columns}.")
            raise ValueError(f"The dataframe must contain the following columns: {required_columns}.")

        formatted_data = []

        # Filter rows where 'Year' is between INITIAL_YEAR + 1 and END_YEAR
        data = data[(data["Year"] >= ExperimentConfig.INITIAL_YEAR + 1) & (data["Year"] <= ExperimentConfig.END_YEAR)]

        for _, row in data.iterrows():
            year = row["Year"]
            sex = row["Sex"]
            race = row["Race"]
            age = row["Age"]
            rate = row[column_name]

            # TODO: add the default value here
            if pd.isna(year) or pd.isna(sex) or pd.isna(race) or pd.isna(age) or pd.isna(rate):
                logger.error(f"Each row must contain non-null values for 'Year', 'Sex', 'Race', 'Age', and '{column_name}'.")
                raise ValueError(f"Each row must contain non-null values for 'Year', 'Sex', 'Race', 'Age', and '{column_name}'.")
            
            if not (0 <= rate <= 1):
                logger.error(f"Invalid {column_name}: {rate}. It must be between 0 and 1.")
                raise ValueError(f"Invalid {column_name}: {rate}. It must be between 0 and 1.")

            composite = f"{sex}_{race}"
            formatted_data.append({"Year": year, "Composite": composite, "Age": age, column_name: rate})
            logger.debug(f"Added to formatted_data: Year={year}, Composite={composite}, Age={age}, {column_name}={rate}")

        logger.info(f"Lookup table for {column_name} loaded successfully as DataFrame.")
        
        return pd.DataFrame(formatted_data)

    
if __name__ == "__main__":
    base_path = "src/experiment_setting/data"
    excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
    death_rate_sheet = "Death_Rate_Data"
    column_name = "Rate"

    try:
        death_lookup = DeathLookupGenerator(base_path, excel_file_name, death_rate_sheet, column_name)
        
        for _, row in death_lookup.lookup_table.iterrows():
            year = row["Year"]
            composite = row["Composite"]
            age = row["Age"]
            rate = row[column_name]
            print(f"Year={year}, Composite={composite}, Rate={rate}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
