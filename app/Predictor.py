import json
import pandas as pd
import xgboost as xgb
from DataParser import DataParser
from Glossary import Glossary

class Predictor:
    def __init__(self, glossary: Glossary):
        self.glossary = glossary

    @staticmethod
    def model_exists(file_prefix: str|None = None):
        path = 'models/'
        if (file_prefix is not None):
            path += file_prefix
        # Check if trained model exists in models/ folder
        # Open the model jsons
        file_path_model = path + 'model.json'
        file_path_model_details = path + 'model_details.json'

        try:
            with open(file_path_model, 'r') as file:
                pass
            file.close()
            with open(file_path_model_details, 'r') as file:
                pass
            file.close()

            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def get_model_details(file_prefix: str|None = None):
        path = 'models/'
        if (file_prefix is not None):
            path += file_prefix
        # Open the model details json
        file_path_model_details = path + 'model_details.json'

        with open(file_path_model_details, 'r') as file:
            model_details = json.load(file)
        file.close()

        return model_details

    def get_model_json(self, file_prefix: str|None = None):
        path = 'models/'
        if (file_prefix is not None):
            path += file_prefix
        # Open the model json
        file_path_model = path + 'model.json'

        with open(file_path_model, 'r') as file:
            model = json.load(file)
        file.close()

        return model

    def predict(self, model_details: dict, file_prefix: str|None = None):
        prefix = 'predicting/'
        model_path = 'models/'
        if (file_prefix is not None):
            prefix += file_prefix
            model_path += file_prefix
        # Get data for prediction
        df_data, student_ids = self.parse_data(model_details, prefix)

        # Load the model
        model_json_path = model_path + 'model.json'
        model           = xgb.XGBClassifier()
        model.load_model(model_json_path)

        # Predict
        predictions = model.predict(df_data)

        # Combine predictions with student ids
        predictions               = pd.DataFrame(predictions, columns=['dropout'])
        predictions['student_id'] = student_ids

        # Save results
        saved_message = self.save_results(predictions, file_prefix)

        return saved_message

    def save_results(self, results: pd.DataFrame, file_prefix: str|None = None):
        path = 'data_out/'
        if (file_prefix is not None):
            path += file_prefix

        # Save predictions to csv
        results.to_csv(path + 'predictions.csv', index=False)

        return self.glossary.get('results') + ' '  + self.glossary.get('saved', True) + ': ' + path + 'predictions.csv'

    def parse_data(self, model_details, file_prefix: str|None = None):
        parsed_data_df = DataParser(self.glossary).parse(
            model_details['data_start_year'],
            model_details['data_end_year'],
            model_details['include_enrolls'],
            True,
            model_details['prediction_epoch'],
            file_prefix,
        )

        # Separate student id from data
        student_id     = parsed_data_df['opisknro']
        parsed_data_df = parsed_data_df.drop(columns=['opisknro'])

        return (parsed_data_df, student_id)
