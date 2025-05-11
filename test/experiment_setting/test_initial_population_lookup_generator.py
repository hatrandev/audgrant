import unittest
from unittest.mock import MagicMock, patch
from src.experiment_setting.initial_population_lookup_generator import InitialPopulationLookupGenerator
from src.experiment_setting.constants import ProbabilityRatesColumnNames
from src.experiment_setting.experiment_config import ExperimentConfig

class TestInitialPopulationLookupGenerator(unittest.TestCase):
    def setUp(self):
        self.base_path = "src/experiment_setting/data"
        self.excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        self.age_sheet_name = "Initial_Population"
        self.sex_sheet_name = "Sex_Average"
        self.race_sheet_name = "Race_Sex_Age"
        self.generator = InitialPopulationLookupGenerator(self.base_path, self.excel_file_name)

    def test_race_data(self):
        try:
            race_data = self.generator.process_initial_population_race_data(self.race_sheet_name)
            self.assertIsNotNone(race_data, "Race data should not be None")
            self.assertIsInstance(race_data, dict, "Race data should be a dictionary")
        except Exception as e:
            self.fail(f"Error processing race data: {e}")

    def test_age_data(self):
        try:
            age_data = self.generator.process_initial_population_age_data(self.age_sheet_name)
            self.assertIsNotNone(age_data, "Age data should not be None")
            self.assertIsInstance(age_data, dict, "Age data should be a dictionary")
        except Exception as e:
            self.fail(f"Error processing age data: {e}")

    def test_sex_data(self):
        try:
            sex_data = self.generator.process_initial_population_sex_data(self.sex_sheet_name)
            self.assertIsNotNone(sex_data, "Sex data should not be None")
            self.assertIsInstance(sex_data, dict, "Sex data should be a dictionary")
        except Exception as e:
            self.fail(f"Error processing sex data: {e}")

if __name__ == "__main__":
    unittest.main()
    