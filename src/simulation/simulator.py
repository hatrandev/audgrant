import os
import csv
from src.simulation.single_year_simulator import SingleYearSimulator
from src.config.simulation_config import ExperimentConfig, ExperimentValid
from src.common.logger import logger


class Simulator:
    def __init__(self, lookup_tables, initial_population, output_file_name=None):
        """
        Initialize the Simulator class.

        :param lookup_tables: Dictionary containing lookup tables for simulation.
        :param initial_population: Initial population DataFrame.
        """
        self.lookup_tables = lookup_tables
        self.population = initial_population
        self.output_file_name = output_file_name if output_file_name else ExperimentConfig.CSV_OUTPUT_FILE

    def simulate(self):
        """
        Simulates the progression of a population over multiple years, summarizing 
        demographic and behavioral statistics for each year and saving the results 
        to a CSV file.

        Returns:
            pandas.DataFrame: The final state of the population after the simulation.
        """
        logger.info("Starting simulation process.")
        output_file = self._initialize_output_file()

        # Simulate for the initial year
        self._summarize_and_save_results(ExperimentConfig.INITIAL_YEAR, output_file)

        # Simulate for subsequent years
        for year in range(ExperimentConfig.INITIAL_YEAR + 1, ExperimentConfig.END_YEAR + 1):
            logger.info(f"Starting simulation for year: {year}")
            self._simulate_single_year(year)
            if ExperimentConfig.START_YEAR_OUTPUT <= year <= ExperimentConfig.END_YEAR_OUTPUT:
                self._summarize_and_save_results(year, output_file)
            logger.info(f"Completed simulation for year: {year}")

        logger.info("Simulation process completed.")
        return self.population

    def _initialize_output_file(self):
        """
        Initialize the output CSV file and write the header row.

        Returns:
            str: Path to the output file.
        """
        output_dir = "test/data/out_data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, self.output_file_name)

        # Define column names
        columns_name_row = [
            "Year", "Total Population", "Child Count", "Adult Count", "Male Proportion",
            "Immigration Proportion", "White Count", "Black Count", "Hispanic Count", "Other Count",
            "Drinking Stage Abs Count", "Drinking Stage Low Count", "Drinking Stage Med Count",
            "Drinking Stage High Count", "Drinking Stage Very High Count"
        ]

        for sex in ["Male", "Female"]:
            for age_group in ["18-34", "35-54", "55+"]:
                columns_name_row += [
                    f"{sex} {age_group} Abs Proportion",
                    f"{sex} {age_group} Low Proportion",
                    f"{sex} {age_group} Med Proportion",
                    f"{sex} {age_group} High Proportion",
                    f"{sex} {age_group} Very High Proportion"
                ]

        """
        for sex in ["Male", "Female"]:
            for age_group in ["18-34", "35-54", "55+"]:
                columns_name_row += [
                    f"{sex} {age_group} Abs Count", f"{sex} {age_group} Abs Proportion",
                    f"{sex} {age_group} Low Count", f"{sex} {age_group} Low Proportion",
                    f"{sex} {age_group} Med Count", f"{sex} {age_group} Med Proportion",
                    f"{sex} {age_group} High Count", f"{sex} {age_group} High Proportion",
                    f"{sex} {age_group} Very High Count", f"{sex} {age_group} Very High Proportion"
                ]

        # Add column names for proportions by age group
        for age_group in ["18-34", "35-54", "55+"]:
            columns_name_row += [
            f"{age_group} Abs Proportion", f"{age_group} Low Proportion",
            f"{age_group} Med Proportion", f"{age_group} High Proportion",
            f"{age_group} Very High Proportion"
            ]

        # Add column names for proportions by sex
        for sex in ["Male", "Female"]:
            columns_name_row += [
            f"{sex} Abs Proportion", f"{sex} Low Proportion",
            f"{sex} Med Proportion", f"{sex} High Proportion",
            f"{sex} Very High Proportion"
            ]

        # Add column names for proportions by race
        for race in ["White", "Black", "Hispanic", "Other"]:
            columns_name_row += [
            f"{race} Abs Proportion", f"{race} Low Proportion",
            f"{race} Med Proportion", f"{race} High Proportion",
            f"{race} Very High Proportion"
            ]
    """
        # Write the header row
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns_name_row)

        return output_file


    def _simulate_single_year(self, year):
        """
        Simulate a single year using the SingleYearSimulator.

        :param year: The year to simulate.
        """
        single_year_simulator = SingleYearSimulator(self.lookup_tables, self.population, year)
        single_year_simulator.simulate_single_year()
        self.population = single_year_simulator.population

    def _summarize_and_save_results(self, year, output_file):
        """
        Summarize the population statistics for a given year and save the results to the CSV file.

        :param year: The year to summarize.
        :param output_file: Path to the output CSV file.
        """
        summary_row = self._summarize_population(year)
        self._validate_population(year, summary_row)
        self._append_to_csv(output_file, summary_row)

    def _summarize_population(self, year):
        """
        Summarize population statistics for a given year.

        :param year: The year to summarize.
        :return: List containing the summary row.
        """
        total_population = len(self.population)
        child_count = len(self.population[self.population["Age"] < 18])
        adult_count = total_population - child_count
        male_count = len(self.population[self.population["Composite"].str.startswith("Male")])
        male_proportion = male_count / total_population if total_population > 0 else 0
        immigration_count = len(self.population[self.population["Immigration"]])
        immigration_proportion = immigration_count / total_population if total_population > 0 else 0

        # Count races
        race_counts = self.population["Composite"].str.split("_").str[1].value_counts()
        race_count_white = race_counts.get("White", 0)
        race_count_black = race_counts.get("Black", 0)
        race_count_hispanic = race_counts.get("Hispanic", 0)
        race_count_other = race_counts.get("Other", 0)

        # Count drinking stages
        drinking_stage_counts = self.population[self.population["Age"] >= 18]["Drinking_Stage"].value_counts()
        drinking_stage_abs = drinking_stage_counts.get("Abs", 0)
        drinking_stage_low = drinking_stage_counts.get("Low", 0)
        drinking_stage_med = drinking_stage_counts.get("Med", 0)
        drinking_stage_high = drinking_stage_counts.get("High", 0)
        drinking_stage_very_high = drinking_stage_counts.get("Very High", 0)

        # Summarize drinking stages by sex and age group
        drinking_stage_summary, drinking_stage_summary_by_age, drinking_stage_summary_by_sex, drinking_stage_summary_by_race = self._summarize_drinking_stages_by_group()

        # Create the summary row
        row = [
            year, total_population, child_count, adult_count, male_proportion,
            immigration_proportion, race_count_white, race_count_black,
            race_count_hispanic, race_count_other, drinking_stage_abs,
            drinking_stage_low, drinking_stage_med, drinking_stage_high,
            drinking_stage_very_high
        ]
        
        for (sex, age_group), summary in drinking_stage_summary.items():
            counts = summary["counts"]
            proportions = summary["proportions"]
            row.extend([
                proportions["Abs"],
                proportions["Low"],
                proportions["Med"],
                proportions["High"],
                proportions["Very High"]
            ])
        
        """
        # Add drinking stage counts and proportions for each sex and age group
        for (sex, age_group), summary in drinking_stage_summary.items():
            counts = summary["counts"]
            proportions = summary["proportions"]
            row.extend([
                counts["Abs"], proportions["Abs"],
                counts["Low"], proportions["Low"],
                counts["Med"], proportions["Med"],
                counts["High"], proportions["High"],
                counts["Very High"], proportions["Very High"]
            ])

        # Add proportions for each age group
        for age_group, summary in drinking_stage_summary_by_age.items():
            proportions = summary["proportions"]
            row.extend([
            proportions["Abs"], proportions["Low"], proportions["Med"],
            proportions["High"], proportions["Very High"]
            ])

        # Add proportions for each sex
        for sex, summary in drinking_stage_summary_by_sex.items():
            proportions = summary["proportions"]
            row.extend([
            proportions["Abs"], proportions["Low"], proportions["Med"],
            proportions["High"], proportions["Very High"]
            ])

        # Add proportions for each race
        for race, summary in drinking_stage_summary_by_race.items():
            proportions = summary["proportions"]
            row.extend([
            proportions["Abs"], proportions["Low"], proportions["Med"],
            proportions["High"], proportions["Very High"]
            ])
        """
        return row

    def _summarize_drinking_stages_by_group(self):
        """
        Summarize drinking stage counts and proportions by sex and age group.

        :return: Dictionary containing drinking stage summaries.
        """
        age_groups = {"18-34": (18, 34), "35-54": (35, 54), "55+": (55, float('inf'))}
        sex_categories = ["Male", "Female"]
        race_categories = ["White", "Black", "Hispanic", "Other"]
        drinking_stage_summary = {}

        # Define all possible drinking stages
        all_drinking_stages = ["Abs", "Low", "Med", "High", "Very High"]

        for sex in sex_categories:
            for age_group, (age_min, age_max) in age_groups.items():
                group_population = self.population[
                    (self.population["Composite"].str.startswith(sex)) &
                    (self.population["Age"] >= age_min) &
                    (self.population["Age"] <= age_max)
                ]
                group_total = len(group_population)

                # Initialize counts and proportions with default values
                drinking_stage_counts = {stage: 0 for stage in all_drinking_stages}
                drinking_stage_proportions = {stage: 0 for stage in all_drinking_stages}

                # Update counts and proportions based on actual data
                actual_counts = group_population["Drinking_Stage"].value_counts().to_dict()
                for stage, count in actual_counts.items():
                    drinking_stage_counts[stage] = count
                    drinking_stage_proportions[stage] = count / group_total if group_total > 0 else 0

                drinking_stage_summary[(sex, age_group)] = {
                    "counts": drinking_stage_counts,
                    "proportions": drinking_stage_proportions
                }
        
        # Summarize drinking stages by age group, sex, and race separately
        drinking_stage_summary_by_age = {}
        drinking_stage_summary_by_sex = {}
        drinking_stage_summary_by_race = {}

        # Summarize by age group
        for age_group, (age_min, age_max) in age_groups.items():
            group_population = self.population[
            (self.population["Age"] >= age_min) & (self.population["Age"] <= age_max)
            ]
            group_total = len(group_population)

            drinking_stage_counts = {stage: 0 for stage in all_drinking_stages}
            drinking_stage_proportions = {stage: 0 for stage in all_drinking_stages}

            actual_counts = group_population["Drinking_Stage"].value_counts().to_dict()
            for stage, count in actual_counts.items():
                drinking_stage_counts[stage] = count
                drinking_stage_proportions[stage] = count / group_total if group_total > 0 else 0

            drinking_stage_summary_by_age[age_group] = {
            "proportions": drinking_stage_proportions
            }

        # Summarize by sex
        for sex in sex_categories:
            group_population = self.population[
            self.population["Composite"].str.startswith(sex)
            ]
            group_total = len(group_population)

            drinking_stage_counts = {stage: 0 for stage in all_drinking_stages}
            drinking_stage_proportions = {stage: 0 for stage in all_drinking_stages}

            actual_counts = group_population["Drinking_Stage"].value_counts().to_dict()
            for stage, count in actual_counts.items():
                drinking_stage_counts[stage] = count
                drinking_stage_proportions[stage] = count / group_total if group_total > 0 else 0

            drinking_stage_summary_by_sex[sex] = {
            "proportions": drinking_stage_proportions
            }

        # Summarize by race
        for race in race_categories:
            group_population = self.population[
            self.population["Composite"].str.contains(f"_{race}")
            ]
            group_total = len(group_population)

            drinking_stage_counts = {stage: 0 for stage in all_drinking_stages}
            drinking_stage_proportions = {stage: 0 for stage in all_drinking_stages}

            actual_counts = group_population["Drinking_Stage"].value_counts().to_dict()
            for stage, count in actual_counts.items():
                drinking_stage_counts[stage] = count
                drinking_stage_proportions[stage] = count / group_total if group_total > 0 else 0

            drinking_stage_summary_by_race[race] = {
            "proportions": drinking_stage_proportions
            }

        return drinking_stage_summary, drinking_stage_summary_by_age, drinking_stage_summary_by_sex, drinking_stage_summary_by_race

    def _validate_population(self, year, summary_row):
        """
        Validate the simulated population against predefined validation data.

        :param year: The year to validate.
        :param summary_row: The summary row for the year.
        """
        validated_population = ExperimentValid.VALIDATION_POP_DICTIONARY.get(year, None)
        if validated_population is not None:
            simulated_population = summary_row[1] * ExperimentConfig.INITIAL_POP_COEFFICIENT
            validation_status = abs(simulated_population - validated_population) / validated_population < 0.01
            logger.info(
                f"YEAR {year} SUMMARY: SIMULATED TOTAL POPULATION: {simulated_population}, "
                f"VALIDATED POPULATION: {validated_population}, \033[91mVALIDATION STATUS: {validation_status}\033[0m"
            )

    def _append_to_csv(self, output_file, row):
        """
        Append a row to the output CSV file.

        :param output_file: Path to the output CSV file.
        :param row: The row to append.
        """
        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
