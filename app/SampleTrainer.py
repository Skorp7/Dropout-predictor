from Glossary import Glossary
from Trainer import Trainer

"""
This class is a sample implementation of the Trainer class. It is used to demonstrate how training works.
"""
class SampleTrainer(Trainer):
    def __init__(self, glossary: Glossary):
        # Use parameters suitable for the sample data
        super().__init__(2023, 2023, True, 2.0, 1.6, glossary)

    def parse_data(self):
        # Fetch data from sample folder
        super().parse_data('samples/sample_')
