import json
import pandas as pd

def file_exists(file_path: str):
    """
    Check if file exists.
    """
    try:
        with open(file_path, 'r') as file:
            pass
        file.close()
    except FileNotFoundError:
        return False

    return True

def is_file_empty(file_path: str):
    """
    Check if existing file is empty.
    """
    with open(file_path, 'r') as file:
        line1 = file.readline()
        if (line1 == ''):
            return True
        pass
    file.close()

    return False

def load_file_as_json(file_path: str):
    """
    Load file as json.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    file.close()

    return data

def save_dataframe_as_csv(dataframe: pd.DataFrame, file_path: str):
    """
    Save pandas DataFrame as csv.
    """
    dataframe.to_csv(file_path, index=False)

def read_csv_to_dataframe(file_path: str, delimiter:str=','):
    """
    Read csv to pandas DataFrame.
    """
    return pd.read_csv(file_path, delimiter=delimiter)

def read_lines(file_path: str):
    """
    Read lines from file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    file.close()

    return lines

def save_as_json(data: dict, file_path: str):
    """
    Save dictionary as json.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    file.close()
