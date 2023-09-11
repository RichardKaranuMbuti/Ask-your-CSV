
import pandas as pd

def read_csv_files_to_dataframes(file_paths):
    """
    Reads a list of CSV files and converts them into pandas DataFrame objects.

    Parameters:
    file_paths (list): List of file paths for CSV files.

    Returns:
    list: List containing pandas DataFrame objects for each CSV file.
    """
    dataframes = []

    for path in file_paths:
        dataframe = pd.read_csv(path)  # Modify this line to read data from other file formats when we also use .xlsx files
        dataframes.append(dataframe)

    return dataframes

