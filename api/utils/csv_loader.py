import csv
from typing import List, Dict


def load_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Load data from a CSV file and return it as a list of dictionaries.

    :param file_path: Path to the CSV file.
    :return: List of dictionaries, where each dictionary represents a row of the CSV file.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at {
                                file_path}. Please provide a valid file path.")
    except Exception as e:
        raise Exception(
            f"An error occurred while loading the CSV file: {str(e)}")
