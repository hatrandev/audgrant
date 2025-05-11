import unittest
from src.experiment_setting.birth_lookup_generator import BirthLookupGenerator
from src.common.logger import logger


class TestBirthLookupGenerator(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment with real data.
        """
        self.base_path = "src/experiment_setting/data"
        self.excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        self.birth_rate_sheet = "Birth"
        self.male_ratio_sheet = "Sex_Ratio_At_Birth"
        self.race_sheet_name = "Race_Sex_Age"

        self.generator = BirthLookupGenerator(self.base_path, self.excel_file_name)

    def test_generate_lookup_table(self):
        """
        Test that the lookup tables for birth rate, male ratio, and race proportions are generated correctly.
        """
        try:
            birth_rate_table, male_ratio_table, race_lookup_under_5_table = self.generator.generate_all_lookup_tables(
                self.birth_rate_sheet, self.male_ratio_sheet, self.race_sheet_name
            )

            self.assertTrue(len(birth_rate_table) > 0, "Birth rate table is empty.")
            self.assertTrue(len(male_ratio_table) > 0, "Male ratio table is empty.")
            self.assertTrue(len(race_lookup_under_5_table) > 0, "Race lookup table is empty.")

            logger.info(f"Birth Rate Table: {birth_rate_table}")
            logger.info(f"Male Ratio Table: {male_ratio_table}")
            logger.info(f"Race Lookup Table: {race_lookup_under_5_table}")

        except Exception as e:
            self.fail(f"Test failed due to an exception: {e}")

    def test_birth_rate_table_content(self):
        """
        Test that the birth rate table contains valid data.
        """
        birth_rate_table, _, _ = self.generator.generate_all_lookup_tables(
            self.birth_rate_sheet, self.male_ratio_sheet, self.race_sheet_name
        )

        for year, birth_rate in birth_rate_table.items():
            self.assertTrue(0 <= birth_rate <= 1, f"Invalid birth rate {birth_rate} for year {year}.")

    def test_male_ratio_table_content(self):
        """
        Test that the male ratio table contains valid data.
        """
        _, male_ratio_table, _ = self.generator.generate_all_lookup_tables(
            self.birth_rate_sheet, self.male_ratio_sheet, self.race_sheet_name
        )

        for year, male_ratio in male_ratio_table.items():
            self.assertTrue(0 <= male_ratio <= 1, f"Invalid male ratio {male_ratio} for year {year}.")

    def test_race_lookup_table_content(self):
        """
        Test that the race lookup table contains valid data.
        """
        _, _, race_lookup_under_5_table = self.generator.generate_all_lookup_tables(
            self.birth_rate_sheet, self.male_ratio_sheet, self.race_sheet_name
        )

        for key, race_proportions in race_lookup_under_5_table.items():
            for race, probability in race_proportions.items():
                self.assertTrue(0 <= probability <= 1, 
                                f"Invalid probability {probability} for race {race} in {key}.")


if __name__ == "__main__":
    unittest.main()
    