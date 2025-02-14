import os
import sys
import pyfiglet as fig
from colorama import init, Fore
from Glossary import Glossary


class TerminalPrinter:
    def __init__(self, glossary: Glossary):
        init(autoreset=True)
        self.glossary = glossary

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def empty_line(self, count: int = 1):
        for _ in range(count):
            print('')

    def banner(self):
        self.clear()
        title = self.glossary.get('title')
        self.yellow(fig.figlet_format(title.upper(), font='small', width=100))

    def info(self):
        self.yellow(self.glossary.get('description'))
        self.empty_line()

    def saved(self, message: str):
        self.yellow(self.glossary.get('saved') + ': ' + message)
        self.empty_line()

    """
    Print details of previously trained model.
    Requires a dictionary with the following keys
    - data_start_year
    - data_end_year
    - include_enrolls
    - prediction_epoch
    - beta_value
    - hyperparameters
    """
    def model_details(self, model_details: dict):
        self.yellow(self.glossary.get('model_details') + ':')

        # Start and end years
        self.yellow('"' + self.glossary.get('data_start_year') + '": ')
        self.print('> ' + str(model_details.get('data_start_year')))
        self.yellow('"' + self.glossary.get('data_end_year') + '": ')
        self.print('> ' + str(model_details.get('data_end_year')))

        # Include enrollments?
        self.yellow('"' + self.glossary.get('enroll_data') + '": ')
        self.print('> ' + str(model_details.get('include_enrolls')))

        # Prediction epoch
        self.yellow('"' + self.glossary.get('prediction_epoch') + '": ')
        self.print('> ' + str(model_details.get('prediction_epoch')))

        # Beta value
        self.yellow('"' + self.glossary.get('beta_value') + '": ')
        self.print('> ' + str(model_details.get('beta_value')))

        # Hyperparameters
        self.yellow(self.glossary.get('hyperparameters') + ':')
        self.print('> ' + str(model_details.get('hyperparameters')))

    def what_to_do(self):
        self.yellow(self.glossary.get('what_to_do'))
        self.empty_line()
        self.yellow('P    ' + self.glossary.get('predict'))
        self.yellow('T    ' + self.glossary.get('train'))
        self.yellow('V    ' + self.glossary.get('validate_env'))
        self.yellow('A    ' + self.glossary.get('test') + ' ' + self.glossary.get('training') + ' ' + self.glossary.get('with_sample_data'))
        self.yellow('B    ' + self.glossary.get('test') + ' ' + self.glossary.get('predicting') + ' ' + self.glossary.get('with_sample_data'))
        self.yellow('Q    ' + self.glossary.get('exit'))

    def yellow(self, message: str):
        print(Fore.LIGHTYELLOW_EX + message)

    def print(self, message: str):
        print(message)

    def error(self, message: str):
        print(Fore.RED + message)
    
