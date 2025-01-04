import json
from Glossary import Glossary

class Predictor:
    def __init__(self, glossary: Glossary):
        self.glossary = glossary

    def model_exists():
        # Check if trained model exists in models/ folder
        # Open the model jsons
        file_path_model = 'models/model.json'
        file_path_model_details = 'models/model_details.json'

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

    def get_model_details():
        # Open the model details json
        file_path_model_details = 'models/model_details.json'

        with open(file_path_model_details, 'r') as file:
            model_details = json.load(file)
        file.close()

        return model_details

    def get_model_json(self):
        # Open the model json
        file_path_model = 'models/model.json'

        with open(file_path_model, 'r') as file:
            model = json.load(file)
        file.close()

        return model

    def predict(self):
        model = self.get_model_json()
        # Load the model

        return self.glossary.get('not_implemented')
