import unittest
from src.experiment_setting.birth_lookup_generator import BirthLookupGenerator
from src.simulation.birth_updater import BirthUpdater


class TestBirthUpdaterWithRealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment with real data.
        This method is called once for the entire test class.
        """
        base_path = "src/experiment_setting/data"
        excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        birth_age_sheet_name = "Birth"
        birth_sex_sheet_name = "Sex_Ratio_At_Birth"
        birth_race_sheet_name = "Race_Sex_Age"

        # Initialize BirthLookupGenerator and generate lookup tables
        cls.birth_lookup_generator = BirthLookupGenerator(base_path, excel_file_name)
        cls.birth_rate_table, cls.male_ratio_table, cls.race_lookup_under_5_table = cls.birth_lookup_generator.generate_all_lookup_tables(
            birth_age_sheet_name, birth_sex_sheet_name, birth_race_sheet_name
        )

        # Initialize BirthUpdater
        cls.birth_updater = BirthUpdater(
            cls.birth_rate_table, cls.male_ratio_table, cls.race_lookup_under_5_table
        )

    def test_generate_new_births(self):
        """
        Test the generation of new births for a specific year.
        """
        total_population = 284968955 
        year = 2001

        new_births = self.birth_updater.generate_new_births(total_population, year)

        num_births = self.birth_updater.compute_new_births(total_population, year)
        self.assertEqual(len(new_births), num_births, "The number of generated births does not match the expected value.")

        for birth in new_births:
            self.assertIn("Age", birth, "Each birth entry must have an 'Age' key.")
            self.assertIn("Gender", birth, "Each birth entry must have a 'Gender' key.")
            self.assertIn("Race", birth, "Each birth entry must have a 'Race' key.")
            self.assertEqual(birth["Age"], 0, "The 'Age' of each birth must be 0.")
            self.assertIn(birth["Gender"], ["Male", "Female"], "The 'Gender' must be either 'Male' or 'Female'.")

        male_count = sum(1 for birth in new_births if birth["Gender"] == "Male")
        female_count = sum(1 for birth in new_births if birth["Gender"] == "Female")
        male_ratio = self.birth_updater.male_ratio_lookup[year]
        self.assertAlmostEqual(
            male_count / len(new_births), male_ratio, delta=0.05,
            msg="The male-to-female ratio does not match the expected value."
        )

        race_counts = {}
        for birth in new_births:
            race = birth["Race"]
            race_counts[race] = race_counts.get(race, 0) + 1

        race_proportions = {race: count / len(new_births) for race, count in race_counts.items()}
        for gender in ["Male", "Female"]:
            expected_race_proportions = self.birth_updater.race_lookup[year][gender]
            for race, expected_proportion in expected_race_proportions.items():
                actual_proportion = race_proportions.get(race, 0)
                self.assertAlmostEqual(
                    actual_proportion, expected_proportion, delta=0.05,
                    msg=f"The proportion of race '{race}' for gender '{gender}' does not match the expected value."
                )


if __name__ == "__main__":
    unittest.main()