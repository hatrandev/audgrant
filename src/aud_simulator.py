from src.initialization.initializer import Initializer
from src.simulation.simulator import Simulator
from src.common.logger import logger
import time

class SimulationRunner:
    def __init__(self, 
                 base_path: str, 
                 excel_file_name: str,
                 excel_transition_file_name: str, 
                 excel_initial_prevalence_file_name: str, 
                 seed=None):
        """
        Initialize the SimulationRunner class.

        :param base_path: The directory path where lookup tables will be generated.
        :param excel_file_name: The name of the Excel file containing input data.
        :param age_distribution_dict: Dictionary with age groups and their proportions.
        :param sex_distribution_dict: Dictionary with age groups and gender ratios.
        :param race_distribution_dict: Dictionary with (age group, gender) and race proportions.
        :param lookup_table_params: Dictionary containing parameters for generating lookup tables.
        :param seed: Optional random seed for reproducibility.
        """
        self.simulation_initializer = Initializer(
            base_path, 
            excel_file_name,
            excel_transition_file_name,
            excel_initial_prevalence_file_name,
            seed
        )

    def run_simulation(self,
                       birth_rate_sheet, 
                       birth_male_ratio_sheet, 
                       birth_race_sheet_name, 
                       death_sheet_name, 
                       death_rate_column_name, 
                       immigration_age_sheet, 
                       immigration_sex_sheet, 
                       immigration_race_sheet, 
                       immigration_rate_sheet,
                       drinking_transition_sheet_name, 
                       initial_population_age_sheet, 
                       initial_population_sex_sheet, 
                       initial_population_race_sheet,
                       initial_population_drinking_sheet,
                       output_file_name=None):
        """
        Run the complete simulation process.
        """

        logger.info("Starting simulation process...")
        start_time = time.time()

        lookup_tables, initial_population = self.simulation_initializer.initialize_simulation(
                                                                                birth_rate_sheet, 
                                                                                birth_male_ratio_sheet, 
                                                                                birth_race_sheet_name, 
                                                                                death_sheet_name, 
                                                                                death_rate_column_name, 
                                                                                immigration_age_sheet, 
                                                                                immigration_sex_sheet, 
                                                                                immigration_race_sheet, 
                                                                                immigration_rate_sheet,
                                                                                drinking_transition_sheet_name, 
                                                                                initial_population_age_sheet, 
                                                                                initial_population_sex_sheet, 
                                                                                initial_population_race_sheet,
                                                                                initial_population_drinking_sheet)

        simulator = Simulator(lookup_tables, initial_population, output_file_name)
        simulated_results = simulator.simulate()

        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_time_minutes = elapsed_time / 60
        logger.info(f"Simulation process completed in {elapsed_time_minutes:.2f} MINUTES.")

        return simulated_results

if __name__ == "__main__":
    # Example usage

    base_path = "test/data/input_data"
    excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
    excel_transition_file_name = "Drinking_Stage_Transition_Probabilities.xlsx"
    excel_initial_prevalence_file_name = "Drinking_Stage_Prevalences_2000.xlsx"
    
    birth_rate_sheet = "Birth"
    birth_male_ratio_sheet = "Sex_Ratio_At_Birth"
    birth_race_sheet_name = "Race_Sex_Age"
    death_sheet_name = "Death_Rate_Data"
    death_rate_column_name = "Rate"
    immigration_age_sheet = "Age_Ratio_All_Years"
    immigration_sex_sheet = "Sex_Ratio_All_Years"
    immigration_race_sheet = "Race_Sex_Age"
    immigration_rate_sheet = "Immigration"
    initial_population_age_sheet = "Initial_Population"
    initial_population_sex_sheet = "Sex_Average"
    initial_population_race_sheet = "Race_Sex_Age"
    drinking_transition_sheet_name = "Drinking_TransitionProbability"
    initial_population_drinking_sheet = "Drinking_Prevalence"

    simulator = SimulationRunner(base_path, excel_file_name, excel_transition_file_name, excel_initial_prevalence_file_name)
    simulated_results = simulator.run_simulation(birth_rate_sheet, 
                                                birth_male_ratio_sheet, 
                                                birth_race_sheet_name, 
                                                death_sheet_name, 
                                                death_rate_column_name, 
                                                immigration_age_sheet, 
                                                immigration_sex_sheet, 
                                                immigration_race_sheet, 
                                                immigration_rate_sheet,
                                                drinking_transition_sheet_name,
                                                initial_population_age_sheet, 
                                                initial_population_sex_sheet, 
                                                initial_population_race_sheet,
                                                initial_population_drinking_sheet,
                                                "simulation_output.csv")
    print("Simulated Results:", simulated_results)

    """
    lst_initial_population_drinking_sheet = ["Drinking_Prevalence_AgeGroup", "Drinking_Prevalence_Sex", "Drinking_Prevalence_Race"]
    for initial_population_drinking_sheet in lst_initial_population_drinking_sheet:
        base_path = "test/data/input_data"
        excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        
        birth_rate_sheet = "Birth"
        birth_male_ratio_sheet = "Sex_Ratio_At_Birth"
        birth_race_sheet_name = "Race_Sex_Age"
        death_sheet_name = "Death_Rate_Data"
        death_rate_column_name = "Rate"
        immigration_age_sheet = "Age_Ratio_All_Years"
        immigration_sex_sheet = "Sex_Ratio_All_Years"
        immigration_race_sheet = "Race_Sex_Age"
        immigration_rate_sheet = "Immigration"
        initial_population_age_sheet = "Initial_Population"
        initial_population_sex_sheet = "Sex_Average"
        initial_population_race_sheet = "Race_Sex_Age"
        drinking_transition_sheet_name = "Drinking_TransProb_ByAgeRaceSex"
        simulator = SimulationRunner(base_path, excel_file_name)
        simulated_results = simulator.run_simulation(birth_rate_sheet, 
                                                birth_male_ratio_sheet, 
                                                birth_race_sheet_name, 
                                                death_sheet_name, 
                                                death_rate_column_name, 
                                                immigration_age_sheet, 
                                                immigration_sex_sheet, 
                                                immigration_race_sheet, 
                                                immigration_rate_sheet,
                                                drinking_transition_sheet_name,
                                                initial_population_age_sheet, 
                                                initial_population_sex_sheet, 
                                                initial_population_race_sheet,
                                                initial_population_drinking_sheet,
                                                "similation__output_" + initial_population_drinking_sheet + ".csv")

    lst_transition_probability_sheet = ["TransitionProbabili0tyByAgeSex03", "TransitionProbabilityByAgeSex8", "TransitionProbabilityOverall03","TransitionProbabilityOverall8"]
    for drinking_transition_sheet_name in lst_transition_probability_sheet:
        base_path = "test/data/input_data"
        excel_file_name = "Data_AUD_Grant_Input_472025.xlsx"
        
        birth_rate_sheet = "Birth"
        birth_male_ratio_sheet = "Sex_Ratio_At_Birth"
        birth_race_sheet_name = "Race_Sex_Age"
        death_sheet_name = "Death_Rate_Data"
        death_rate_column_name = "Rate"
        immigration_age_sheet = "Age_Ratio_All_Years"
        immigration_sex_sheet = "Sex_Ratio_All_Years"
        immigration_race_sheet = "Race_Sex_Age"
        immigration_rate_sheet = "Immigration"
        initial_population_age_sheet = "Initial_Population" 
        initial_population_sex_sheet = "Sex_Average"
        initial_population_race_sheet = "Race_Sex_Age"
        initial_population_drinking_sheet = "Drinking_Prevalence"
        simulator = SimulationRunner(base_path, excel_file_name)
        simulated_results = simulator.run_simulation(birth_rate_sheet, 
                                                birth_male_ratio_sheet, 
                                                birth_race_sheet_name, 
                                                death_sheet_name, 
                                                death_rate_column_name, 
                                                immigration_age_sheet, 
                                                immigration_sex_sheet, 
                                                immigration_race_sheet, 
                                                immigration_rate_sheet,
                                                drinking_transition_sheet_name,
                                                initial_population_age_sheet, 
                                                initial_population_sex_sheet, 
                                                initial_population_race_sheet,
                                                initial_population_drinking_sheet,
                                                "similation_output_" + drinking_transition_sheet_name + ".csv")

        """