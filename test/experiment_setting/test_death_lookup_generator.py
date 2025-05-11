import unittest
import pandas as pd
from src.experiment_setting.death_lookup_generator import DeathLookupGenerator

class TestDeathLookupGenerator(unittest.TestCase):
    def setUp(self):
        self.base_path = "src/experiment_setting/data"
        self.excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        self.sheet_name = "Death_Rate_Data"
        self.column_name = "Rate"

    def test_load_lookup_table_success(self):
        generator = DeathLookupGenerator(self.base_path, self.excel_file_name, self.sheet_name, self.column_name)
        self.assertIsInstance(generator.lookup_table, dict)
        self.assertGreater(len(generator.lookup_table), 0)

    def test_get_rate(self):
        generator = DeathLookupGenerator(self.base_path, self.excel_file_name, self.sheet_name, self.column_name)
        rate = generator.get_rate(2001, "Female", "Black", 0)
        self.assertAlmostEqual(rate, 0.0124721946194768, places=4)

    def test_lookup_table_structure(self):
        generator = DeathLookupGenerator(self.base_path, self.excel_file_name, self.sheet_name, self.column_name)
        for year, sex_dict in generator.lookup_table.items():
            self.assertIsInstance(sex_dict, dict)
            for sex, race_dict in sex_dict.items():
                self.assertIsInstance(race_dict, dict)
                for race, age_dict in race_dict.items():
                    self.assertIsInstance(age_dict, dict)
                    for age, rate in age_dict.items():
                        self.assertIsInstance(rate, (float, int))

if __name__ == "__main__":
    unittest.main()
