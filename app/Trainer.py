import json
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, recall_score, precision_score, cohen_kappa_score, fbeta_score
from DataParser import DataParser
from Glossary import Glossary
from scripts.hyper_optimising import find_best_params

class Trainer:

    DEFAULT_BETA_VALUE       = 1.6 # Beta value to be used in F-score to optimise hyperparameters (1.6 favours recall over precision)
    DEFAULT_ENROLLS_INCLUDED = False # Whether to include enrollments data in the training.
    DEFAULT_PREDICTION_EPOCH = 1.5 # For how many years students have studied before predicting

    def __init__(self, data_start_year: int, data_end_year: int, include_enrolls: bool, prediction_epoch: float, beta_value: float, glossary: Glossary):
        self.data_start_year  = data_start_year
        self.data_end_year    = data_end_year
        self.include_enrolls  = include_enrolls
        self.prediction_epoch = prediction_epoch
        self.beta_value       = beta_value
        self.glossary         = glossary
        self.fixed_params     = None
        self.parsed_data_df   = None
        self.hyperparameters  = None

    def parse_data(self, file_prefix: str|None = None):
        self.parsed_data_df = DataParser(self.glossary).parse(
            self.data_start_year,
            self.data_end_year,
            self.include_enrolls,
            self.prediction_epoch,
            file_prefix,
        )

        return self.glossary.get('data_parsed') + '... '

    def optimise_hyperparameters(self, data: pd.DataFrame, target: pd.DataFrame):
        self.fixed_params = {
            'booster': 'gbtree',
            'eval_metric': 'logloss',
            'objective': 'binary:logistic',
            'tree_method': 'exact', # Exact is slower. This data is so small it can be used.
            'base_score': 0.45, # The percentage of dropouts (~ according to data of students started 2017-2022)
            'n_estimators': 80, # Number of boosting rounds.
        }

        return find_best_params(data, target, self.beta_value, self.fixed_params)

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
    def train(self):
        if self.parsed_data_df is None:
            raise RuntimeError('Data not parsed yet. Parse data before training.')

        data_df = self.parsed_data_df

        # Define the target variable
        target = data_df['dropout']
        # Remove the target variable from the data frame
        data = data_df.drop(columns=['dropout'])

        # Optimise hyperparameters
        best_params = self.optimise_hyperparameters(data, target)
        # Add fixed parameters to the best parameters to get all hyperparameters.
        best_params.update(self.fixed_params)
        self.hyperparameters = best_params

        # Train the model
        model = xgb.XGBClassifier(**best_params)
        model.fit(data, target)

        # Save the model
        self.save_model(model)

        # Show training results
        training_results                    = self.get_training_metrics(model, data, target)
        training_results['hyperparameters'] = best_params

        return training_results

    def save_model(self, model):
        # Save model
        model.save_model('models/model.json')

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
        with open('models/model_details.json', 'w') as f:
            json.dump(model_details, f, indent=4)
        f.close()
