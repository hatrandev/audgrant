import unittest
from src.initialization.initial_population_generator import PopulationInitializer
from src.experiment_setting.initial_population_lookup_generator import InitialPopulationLookupGenerator
from src.common.logger import logger

class TestPopulationInitializer(unittest.TestCase):
    def setUp(self):
        self.base_path = "src/experiment_setting/data"
        self.excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        self.age_sheet_name = "Initial_Population"
        self.sex_sheet_name = "Sex_Average"
        self.race_sheet_name = "Race_Sex_Age"
        self.lookup_generator = InitialPopulationLookupGenerator(self.base_path, self.excel_file_name)
        self.age_distribution = self.lookup_generator.process_initial_population_age_data(sheet_name=self.age_sheet_name)
        self.sex_distribution = self.lookup_generator.process_initial_population_sex_data(sheet_name=self.sex_sheet_name)
        self.race_distribution = self.lookup_generator.process_initial_population_race_data(sheet_name=self.race_sheet_name)

    def test_population_generation(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        population = initializer.generate_initial_population()
        self.assertEqual(len(population), initializer.total_population)

    def test_invalid_age_distribution(self):
        invalid_age_distribution = {"0-4": 0.5, "5-9": 0.6}
        with self.assertRaises(ValueError):
            PopulationInitializer(invalid_age_distribution, self.sex_distribution, self.race_distribution)

    def test_invalid_sex_distribution(self):
        invalid_sex_distribution = {"0-4": 1.2}
        with self.assertRaises(ValueError):
            PopulationInitializer(self.age_distribution, invalid_sex_distribution, self.race_distribution)

    def test_invalid_race_distribution(self):
        invalid_race_distribution = {("0-4", "Male"): {"Race1": 0.6, "Race2": 0.6}}
        with self.assertRaises(ValueError):
            PopulationInitializer(self.age_distribution, self.sex_distribution, invalid_race_distribution)

    def test_population_adjustment(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        population = initializer.generate_initial_population()
        adjustment = initializer.total_population - len(population)
        adjusted_population = initializer._adjust_population(population, adjustment)
        self.assertEqual(len(adjusted_population), initializer.total_population)

    def test_age_group_assignment(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        age_group = initializer._get_age_group(25)
        self.assertEqual(age_group, "25 to 29 years")

    def test_random_seed_reproducibility(self):
        initializer1 = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution, seed=42)
        initializer2 = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution, seed=42)
        population1 = initializer1.generate_initial_population()
        population2 = initializer2.generate_initial_population()

        self.assertEqual(population1, population2, "Populations are not identical")

    def test_missing_race_distribution(self):
        incomplete_race_distribution = {("0-4", "Male"): {"Race1": 0.5}}
        with self.assertRaises(ValueError):
            PopulationInitializer(self.age_distribution, self.sex_distribution, incomplete_race_distribution)

    def test_population_size_after_adjustment(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        population = initializer.generate_initial_population()
        adjustment = 10
        adjusted_population = initializer._adjust_population(population, adjustment)
        self.assertEqual(len(adjusted_population), initializer.total_population + adjustment)

    def test_gender_assignment(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        population = initializer.generate_initial_population()
        genders = [person['Gender'] for person in population]
        self.assertTrue(all(gender in ['Male', 'Female'] for gender in genders))

    def test_race_assignment(self):
        initializer = PopulationInitializer(self.age_distribution, self.sex_distribution, self.race_distribution)
        population = initializer.generate_initial_population()
        races = [person['Race'] for person in population]
        self.assertTrue(all(isinstance(race, str) for race in races))

if __name__ == "__main__":
    unittest.main()
