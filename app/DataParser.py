import pandas as pd
from scripts.parse_students import parse_students
from scripts.cut_and_prepare_data import cut_data
from Glossary import Glossary

class DataParser:
    def __init__(self, glossary: Glossary):
        self.glossary = glossary

    """
    Parse data to be ready for training the model.
    Takes data from files data_in/{prefix}{year}_**** and saves to csv data_processed/data_ready_for_model/{file_prefix}{epochs}_prds_****.csv.
    """
    def parse(self, data_start_year: int, data_end_year: int, include_enrolls: bool, data_for_prediction: bool, prediction_epoch: float, file_prefix: str|None = None):
        years = range(data_start_year, data_end_year + 1)
        self.parse_students_data(years, include_enrolls, data_for_prediction, file_prefix)
        self.combine_yearly_datasets(years, include_enrolls, file_prefix)
        ready_data_df = self.cut_data(prediction_epoch, years, include_enrolls, file_prefix)

        return ready_data_df

    """
    Cut data after periods and prepare it for training. Save to csv data_processed/data_ready_for_model/{file_prefix}{epochs}_prds_****.csv.
    Also return the dataframe.
    """
    def cut_data(self, prediction_epoch: float, years: list, include_enrolls: bool, file_prefix: str|None = None):
        return cut_data(prediction_epoch, years, include_enrolls, file_prefix)

    """
    Parse students, courses and enrollments and save to csv.
    """
    def parse_students_data(self, years: list, include_enrolls: bool, data_for_prediction: bool, file_prefix: str|None = None):
        parse_students(years, include_enrolls, data_for_prediction, file_prefix)

    """
    Combine yearly datasets into one.
    Saves processed data to data_processed/{prefix}combined_{start_year}-{end_year}.csv.
    """
    def combine_yearly_datasets(self, years: list, include_enrolls: bool, file_prefix: str|None = None):
        path = 'data_processed/'
        if (file_prefix is not None):
            path += file_prefix
        df_combined = pd.DataFrame()

        for year in years:
            year_file = path + str(year) + '_processed.csv'

            # Combine this year's data into the combined dataframe using the first row of csv as header
            df_year     = pd.read_csv(year_file, delimiter=',')
            df_combined = pd.concat([df_combined, df_year], ignore_index=True)

        # Save the combined data
        file_name = 'combined_'
        if (include_enrolls):
            file_name += 'enrolls_'
        file_name += str(years[0]) + '-' + str(years[-1]) + '.csv'
        df_combined.to_csv(path + file_name, index=False)
