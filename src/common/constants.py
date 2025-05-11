class Common:
    MALE = 'Male'
    FEMALE = 'Female'

    AGE = 'Age'
    SEX = 'Sex'
    RACE = 'Race'

class ProbabilityRatesColumnNames:
    YEAR_COLUMN = "Year"
    TOTAL_POPULATION_COLUMN = "Total_Population"
    POPULATION_COUNT_COLUMN = "Population_Count"
    AGE_GROUP_COLUMN = "Age_Group"
    SEX_COLUMN = Common.SEX
    RACE_COLUMN = Common.RACE
    RACE_PROPORTION_COLUMN = "Race_Proportion"
    IMMIGRATION_RATE_COLUMN = "Immigration_Rate"

    TOTAL_COLUMN = "Total"
    AGE_COLUMN = Common.AGE
    AGE_RATIO_COLUMN = "Age_Ratio"
    AGE_RATIO_COLUMN_IMMIGRATION = "Ratio_of_Year"

    TOTAL_MALE_COLUMN = "Total_Male"
    MALE_RATIO_COLUMN = "Male_Ratio"

    AGE_KEY = Common.AGE
    GENDER_KEY = Common.SEX
    RACE_KEY = Common.RACE

    MALE = Common.MALE
    FEMALE = Common.FEMALE

class InitializationConstants:
    AGE_KEY = Common.AGE
    GENDER_KEY = Common.SEX
    RACE_KEY = Common.RACE
    ALIVE_KEY = 'Alive'
    IMMIGRATION_KEY = "Immigration"
    AGE_GROUP_KEY = "Age_Group"
    ID_KEY = "ID"
    RNG_KEY = "RNG"

    MALE = Common.MALE
    FEMALE = Common.FEMALE
    DRINKING_STATUS_KEY = "Drinking_Status"
    DRINKING_STAGE_KEY = "Drinking_Stage"

    AGE_GROUPS = [
        (0, 4, 'Under 5 years'),
        (5, 9, '5 to 9 years'),
        (10, 14, '10 to 14 years'),
        (15, 19, '15 to 19 years'),
        (20, 24, '20 to 24 years'),
        (25, 29, '25 to 29 years'),
        (30, 34, '30 to 34 years'),
        (35, 39, '35 to 39 years'),
        (40, 44, '40 to 44 years'),
        (45, 49, '45 to 49 years'),
        (50, 54, '50 to 54 years'),
        (55, 59, '55 to 59 years'),
        (60, 64, '60 to 64 years'),
        (65, 69, '65 to 69 years'),
        (70, 74, '70 to 74 years'),
        (75, 79, '75 to 79 years'),
        (80, 84, '80 to 84 years'),
        (85, float('inf'), '85 years and over'),
    ]

class UpdaterColumnNames:
    AGE_KEY = Common.AGE
    GENDER_KEY = Common.SEX
    RACE_KEY = Common.RACE
    ALIVE_KEY = 'Alive'
    IMMIGRATION_KEY = "Immigration"
    AGE_GROUP_KEY = "Age_Group"
    ID_KEY = "ID"
    RNG_KEY = "RNG"
    MALE = Common.MALE
    FEMALE = Common.FEMALE
    DRINKING_STATUS_KEY = "Drinking_Status"
    DRINKING_STAGE_KEY = "Drinking_Stage"