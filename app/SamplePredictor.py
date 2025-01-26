from Glossary import Glossary
from Predictor import Predictor
from ProgressLogger import ProgressLogger

"""
This class is a sample implementation of the Predictor class. It is used to demonstrate how predicting works.
"""
class SamplePredictor(Predictor):
    def __init__(self, glossary: Glossary, logger: ProgressLogger):
        super().__init__(glossary, 2024, logger)

    @staticmethod
    def model_exists():
        return Predictor.model_exists('samples/sample_')

    def predict(self):
        if not self.model_exists():
            raise Exception('Sample model does not exist. Train the model first.')
        # Get sample model details
        model_details = Predictor.get_model_details('samples/sample_')
        # Predict
        return super().predict(model_details, 'samples/sample_')
