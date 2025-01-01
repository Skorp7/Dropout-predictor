from DataParser import DataParser
from Glossary import Glossary

class Trainer:

    DEFAULT_BETA_VALUE       = 1.6 # Beta value to be used in F-score to optimise hyperparameters (1.6 favours recall over precision)
    DEFAULT_ENROLLS_INCLUDED = False # Whether to include enrollments data in the training.
    DEFAULT_PREDICTION_EPOCH = 2.0 # For how many years students have studied before predicting

    def __init__(self, data_start_year: int, data_end_year: int, prediction_epoch: float, beta_value: float, glossary: Glossary):
        self.data_start_year  = data_start_year
        self.data_end_year    = data_end_year
        self.prediction_epoch = prediction_epoch
        self.beta_value       = beta_value
        self.glossary         = glossary
        self.parsed_data_df   = None

    def parse_data(self, file_prefix: str|None = None):
        self.parsed_data_df = DataParser(self.glossary).parse(self.data_start_year, self.data_end_year, self.prediction_epoch, file_prefix)

        return self.glossary.get('data_parsed') + '... '

    def train(self):
        if self.parsed_data_df is None:
            raise RuntimeError('Data not parsed yet. Parse data before training.')
        return self.glossary.get('not_implemented')
        
