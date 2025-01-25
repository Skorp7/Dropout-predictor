import numpy as np
import warnings
from Glossary import Glossary
from Predictor import Predictor
from SamplePredictor import SamplePredictor
from SampleTrainer import SampleTrainer
from TerminalPrinter import TerminalPrinter
from Trainer import Trainer
from Validator import Validator

warnings.filterwarnings('ignore')

def get_lang():
    # Ask for language
    lang_code = input('Select language by typing "en" for English or "fi" for Finnish: ')

    return lang_code

def main_program(glossary: Glossary):
    printer = TerminalPrinter(glossary)
    # Welcome
    printer.banner()
    # Print info
    printer.info()
    # Ask for action
    what_to_do(printer, glossary)

def what_to_do(printer: TerminalPrinter, glossary: Glossary):
    printer.what_to_do()
    ask_for_action(printer, glossary)

def ask_for_action(printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            # Ask for input
            train_or_predict = input('> ').lower()
            check_for_quitting(train_or_predict, printer)
            if train_or_predict == 't':
                # TRAIN
                printer.empty_line()
                printer.yellow(glossary.get('training_instructions'))
                printer.yellow(glossary.get('press_enter_to_continue'))
                input('>')
                (data_start_year, data_end_year) = ask_for_training_years(printer, glossary)
                printer.saved(str(data_start_year) + ' - ' + str(data_end_year))
                enroll_data = ask_for_enroll_data(data_start_year, printer, glossary)
                printer.saved(str(enroll_data))
                prediction_epoch = ask_for_prediction_epoch(printer, glossary)
                printer.saved(str(prediction_epoch))
                beta_value = ask_for_beta_value(printer, glossary)
                printer.saved(str(beta_value))
                printer.print(glossary.get('training_in_progress') + '... (' + glossary.get('interrupt_by') + ' Ctrl + C)')
                try:
                    trainer  = Trainer(data_start_year, data_end_year, enroll_data, prediction_epoch, beta_value, glossary)
                    messages = trainer.parse_data()
                    printer.print(messages)
                    messages = trainer.train()
                    printer.empty_line()
                    printer.yellow(glossary.get('training_results') + ':')
                    # print message dict nicely
                    for key, value in messages.items():
                        printer.print(f'{key}: {value}')
                    printer.empty_line()
                    printer.empty_line()
                except Exception as e:
                    printer.error(str(e))
                what_to_do(printer, glossary)
            elif train_or_predict == 'p':
                # PREDICT
                printer.empty_line()
                approved_model_details = ask_for_model_approval(printer, glossary)
                if (approved_model_details is not None):
                    printer.empty_line()
                    printer.print(glossary.get('predicting_in_progress') + '...')
                    predictor = Predictor(glossary)
                    try:
                        messages = predictor.predict(approved_model_details)
                    except Exception as e:
                        printer.error(str(e))
                    printer.yellow(messages)
                    printer.empty_line()
                    exit()
                else:
                    what_to_do(printer, glossary)
            elif train_or_predict == 'v':
                # VALIDATE ENVIRONMENT
                printer.empty_line()
                validator = Validator(glossary)
                printer.print(glossary.get('validating') + '...')
                result = validator.validate_environment()
                printer.print(result)
                printer.empty_line()
                what_to_do(printer, glossary)
            elif train_or_predict == 'a':
                # TEST TRAINING WITH SAMPLE DATA
                printer.empty_line()
                printer.print(glossary.get('training_in_progress') + '... (' + glossary.get('interrupt_by') + ' Ctrl + C)')
                try:
                    trainer  = SampleTrainer(glossary)
                    messages = trainer.parse_data()
                    printer.print(messages)
                    messages = trainer.train()
                    printer.empty_line()
                    printer.yellow(glossary.get('training_results') + ':')
                    # print message dict nicely
                    for key, value in messages.items():
                        printer.print(f'{key}: {value}')
                except Exception as e:
                    printer.error(str(e))
                printer.empty_line()
                what_to_do(printer, glossary)
            elif train_or_predict == 'b':
                # TEST PREDICTING WITH SAMPLE DATA
                printer.empty_line()
                printer.print(glossary.get('predicting_in_progress') + '...')
                predictor = SamplePredictor(glossary)
                try:
                    messages = predictor.predict()
                except Exception as e:
                    printer.error(str(e))
                printer.yellow(messages)
                printer.empty_line()
                what_to_do(printer, glossary)
            else:
                raise ValueError
        except ValueError:
            printer.error(glossary.get('invalid_input') + ': ' + train_or_predict)

def ask_for_training_years(printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            printer.yellow(glossary.get('data_start_year'))
            data_start_year = input('> ').lower()
            check_for_quitting(data_start_year, printer)
            printer.yellow(glossary.get('data_end_year'))
            data_end_year = input('> ').lower()
            check_for_quitting(data_end_year, printer)

            if data_end_year == '':
                # When end year is not given, suppose only data of one year is provided.
                data_end_year = data_start_year

            data_start_year = int(data_start_year)
            data_end_year   = int(data_end_year)

            if (
                data_start_year > 2016
                and data_end_year > 2016
                and data_end_year >= data_start_year
            ):
                return (int(data_start_year), int(data_end_year))
            else:
                raise ValueError
        except ValueError:
            printer.error(glossary.get('invalid_input'))

def ask_for_prediction_epoch(printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            printer.yellow(glossary.get('prediction_epoch'))
            prediction_epoch = input('> ').lower()
            check_for_quitting(prediction_epoch, printer)

            if (prediction_epoch == ''):
                return Trainer.DEFAULT_PREDICTION_EPOCH
            
            prediction_epoch = float(prediction_epoch)

            if (prediction_epoch in np.arange(1, 4, 0.5)):
                return prediction_epoch
            else:
                raise ValueError
        except ValueError:
            printer.error(glossary.get('invalid_input'))

def ask_for_beta_value(printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            printer.yellow(glossary.get('beta_value') + '. ' + glossary.get('beta_value_info'))
            beta_value = input('> ').lower()
            check_for_quitting(beta_value, printer)

            if (beta_value == ''):
                return Trainer.DEFAULT_BETA_VALUE

            beta_value = float(beta_value)

            if (beta_value in np.arange(0, 10.1, 0.1)):
                return beta_value
            else:
                raise ValueError
        except ValueError:
            printer.error(glossary.get('invalid_input'))

def ask_for_enroll_data(data_start_year, printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            printer.yellow(glossary.get('enroll_data'))
            enroll_data = input('> ').lower()
            check_for_quitting(enroll_data, printer)
            if (enroll_data == ''):
                return Trainer.DEFAULT_ENROLLS_INCLUDED

            if (enroll_data == 'y' and data_start_year >= 2020):
                return True
            elif (enroll_data == 'n'):
                return False
            else:
                raise ValueError
        except ValueError:
            printer.error(glossary.get('invalid_input'))

"""
Find the saved model.
Ask for approval to use the model.
If approved, return model retails. If not approved, return None.
"""
def ask_for_model_approval(printer: TerminalPrinter, glossary: Glossary):
    while True:
        try:
            if (Predictor.model_exists()):
                printer.yellow(glossary.get('model_found'))
                model_details = Predictor.get_model_details()
                printer.model_details(model_details)
                printer.yellow(glossary.get('model_approval'))
                model_approval = input('> ').lower()
                check_for_quitting(model_approval, printer)
                if (model_approval == 'y'):
                    return model_details
                elif (model_approval == 'n'):
                    return None
                else:
                    raise ValueError
            else:
                printer.yellow(glossary.get('no_model'))
                # Ask again what to do
                what_to_do(printer, glossary)
        except ValueError:
            printer.error(glossary.get('invalid_input'))

def check_for_quitting(input: str, printer: TerminalPrinter):
    if input == 'q':
        printer.empty_line()
        exit()

def main():
    printer = None
    try:
        lang_code = get_lang()
        glossary = Glossary(lang_code)

        # Start the main program
        main_program(glossary)
    except Exception as e:
        if (printer):
            printer.error(f'Error: {e}')
        else:
            print(f'Error: {e}')
        exit()

if __name__ == "__main__":
    main()
