import os
import sys
import pyfiglet as fig
from colorama import init, Fore
from Glossary import Glossary


class TerminalPrinter:
    def __init__(self, glossary: Glossary):
        init(autoreset=True)
        self.glossary = glossary

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def empty_line(self):
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
    
