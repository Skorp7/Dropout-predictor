import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, recall_score, precision_score, cohen_kappa_score, fbeta_score
import FileHandler
from DataParser import DataParser
from Glossary import Glossary
from ProgressLogger import ProgressLogger
from scripts.hyper_optimising import find_best_params

class Trainer:

    DEFAULT_BETA_VALUE       = 1.6 # Beta value to be used in F-score to optimise hyperparameters (1.6 favours recall over precision)
    DEFAULT_ENROLLS_INCLUDED = False # Whether to include enrollments data in the training.
    DEFAULT_PREDICTION_EPOCH = 1.5 # For how many years students have studied before predicting
    TRIALS                   = 500 # Number of trials for hyperparameter optimisation

    def __init__(self, data_start_year: int, data_end_year: int, include_enrolls: bool, prediction_epoch: float, beta_value: float, glossary: Glossary, logger: ProgressLogger):
        self.data_start_year  = data_start_year
        self.data_end_year    = data_end_year
        self.include_enrolls  = include_enrolls
        self.prediction_epoch = prediction_epoch
        self.beta_value       = beta_value
        self.glossary         = glossary
        self.fixed_params     = None
        self.parsed_data_df   = None
        self.hyperparameters  = None
        self.logger           = logger

    @staticmethod
    def required_files_info(start_year: int, end_year: int, include_enrolls: bool):
        years    = range(start_year, end_year + 1)
        filelist = []
        for year in years:
            filelist.append(str(year) + '_students.csv')
            filelist.append(str(year) + '_credits.csv')
            if (include_enrolls):
                filelist.append(str(year) + '_enrollments.csv')

        return filelist

    def parse_data(self, file_prefix: str|None = None):
        self.logger.update()

        path = 'training/'
        if (file_prefix is not None):
            path += file_prefix
        self.parsed_data_df = DataParser(self.glossary, self.logger).parse(
            self.data_start_year,
            self.data_end_year,
            self.include_enrolls,
            False, # This not data for prediction, but for training.
            self.prediction_epoch,
            path,
        )
        self.logger.update()

        return self.glossary.get('data_parsed') + '... '

    def optimise_hyperparameters(self, data: pd.DataFrame, target: pd.DataFrame, trials: int):
        self.fixed_params = {
            'booster': 'gbtree',
            'eval_metric': 'logloss',
            'objective': 'binary:logistic',
            'tree_method': 'exact', # Exact is slower. This data is so small it can be used.
            'base_score': 0.45, # The percentage of dropouts (~ according to data of students started 2017-2022)
            'n_estimators': 80, # Number of boosting rounds.
        }

        return find_best_params(data, target, self.beta_value, self.fixed_params, trials, self.logger)

    def get_training_metrics(self, model, data, target):
        # Predict
        y_pred = model.predict(data)

        # Calculate metrics
        accuracy    = accuracy_score(target, y_pred)
        recall      = recall_score(target, y_pred)
        precision   = precision_score(target, y_pred)
        fbeta       = fbeta_score(target, y_pred, beta=self.beta_value)
        cohen_kappa = cohen_kappa_score(target, y_pred)

        return {
            'accuracy': accuracy,
            'recall': recall,
            'precision': precision,
            'fbeta_score': fbeta,
            'kappa': cohen_kappa,
        }

    """
    Train the model using XGBoost.
    Training includes hyperparameter optimising.
    Training uses the whole data set for training. So, training accuracy/recall/other metrics are not good measures of model performance.
    Model validation is done when tuning hyperparameters.
    """
    def train(self, file_prefix: str|None = None, trials: int|None = None):
        if self.parsed_data_df is None:
            raise RuntimeError('Data not parsed yet. Parse data before training.')

        if trials is None:
            trials = self.TRIALS

        data_df = self.parsed_data_df

        # Define the target variable
        target = data_df['dropout']
        # Remove the target variable from the data frame
        data = data_df.drop(columns=['dropout'])
        self.logger.update()
        # Optimise hyperparameters
        best_params = self.optimise_hyperparameters(data, target, trials)
        # Add fixed parameters to the best parameters to get all hyperparameters.
        best_params.update(self.fixed_params)
        self.hyperparameters = best_params

        self.logger.update()
        # Train the model
        model = xgb.XGBClassifier(**best_params)
        model.fit(data, target)

        # Save the model
        self.save_model(model, file_prefix)

        self.logger.update()

        # Show training results
        training_results                    = self.get_training_metrics(model, data, target)
        training_results['hyperparameters'] = best_params

        return training_results

    def save_model(self, model, file_prefix: str|None = None):
        path = 'models/'
        if (file_prefix is not None):
            path += file_prefix
        # Save model
        model.save_model(path + 'model.json')

        # Save training details to json too
        model_details = {
            'data_start_year': self.data_start_year,
            'data_end_year': self.data_end_year,
            'include_enrolls': self.include_enrolls,
            'prediction_epoch': self.prediction_epoch,
            'beta_value': self.beta_value,
        }
        model_details['hyperparameters'] = self.hyperparameters
        # Save
        FileHandler.save_as_json(model_details, path + 'model_details.json')
