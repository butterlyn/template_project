# standard libary imports
import os
import time
from typing import (
    Union,
    Callable,
    Type,
)
import logging
# third party imports
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from alive_progress import alive_bar
# local imports
from ..helpers import (
    flatten_dict,
    count_final_values_in_dict,
)
from utils import LoadersDictTypeHint


# %%
# Functions

def _time_how_long_to_load_dataframe(
    loader: Union[Callable, Type],
    file_path_to_load: str,
) -> float:
    """time how long it takes to load a dataframe from a file"""
    start_time: float = time.time()
    loader(file_path_to_load)
    end_time: float = time.time()
    return (end_time - start_time)


def time_dataframe_loaders(
    data_frame_loaders: LoadersDictTypeHint,
    files_path_to_load_given_the_filetype: dict[str, str],
    progress_bar_enabled: bool = True,
) -> None:
    """time how long it takes to load a file using difference dataframe loaders"""
    # count of loaders for progress bar
    loader_count: int = count_final_values_in_dict(data_frame_loaders)

    with alive_bar(total=loader_count) if progress_bar_enabled else None as bar:
        # flatten the data_frame_loaders dictionary to get the loaders and labels
        flattened_data_frame_loaders: dict[str, Union[Callable, Type]] = flatten_dict(
            data_frame_loaders,
            parent_key='LOAD_TIME',
            sep='-',
        )

        # store the load times
        load_times: dict[str, float] = {}

        # time how long it takes to load each dataframe from a file
        label: str
        file_type: str
        loader: Union[Callable, Type]
        for file_type in data_frame_loaders.keys():
            file_path_to_load: str = files_path_to_load_given_the_filetype[file_type]
            for label, loader in flattened_data_frame_loaders.items():
                logging.debug(f'Loading {label}...')
                load_time: float = _time_how_long_to_load_dataframe(
                    loader=loader,
                    file_path_to_load=file_path_to_load,
                )
                load_times[label] = load_time
                bar()

    # return the load times
    return load_times


def sort_load_times(load_times: dict[str, float]) -> dict[str, float]:
    """sort the load times"""
    logging.debug('Sorting load times...')
    return dict(
        sorted(
            load_times.items(),
            key=lambda item: item[1]
        )
    )


def print_load_times(load_times: dict[str, float]) -> None:
    """print the load times"""
    logging.debug('Printing load times...')
    load_time: float
    label: str
    for label, load_time in load_times.items():
        print(f'{label}: {load_time}')


def generate_data(
    num_rows: int,
    columns: str,
    csv_file: str,
    parquet_file: str
) -> None:
    """
    Generate random data and write it to CSV and Parquet files.

    Args:
        num_rows (int): The number of rows to generate.
        columns (list): A list of column names.
        csv_file (str): The name of the CSV file to write.
        parquet_file (str): The name of the Parquet file to write.
    """
    # Generate random data
    data = np.random.rand(num_rows, len(columns))

    # Create DataFrame object
    df = pd.DataFrame(data, columns=columns)

    # Write DataFrame to CSV file
    df.to_csv(csv_file, index=False)

    # Create Table object
    table = pa.Table.from_arrays(
        [pa.array(data[:, i]) for i in range(len(columns))],
        names=columns
    )

    # Write Table to Parquet file
    pq.write_table(table, parquet_file)


# %%
# Process functions

def main():
    files_path_to_load_given_the_filetype: dict[str, str] = {
        'parquet': 'large_file.parquet',
        'csv': 'large_file.csv',
    }

    logging.info('Generating mock data...')
    generate_data(
        num_rows=10000,
        columns=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
        csv_file=files_path_to_load_given_the_filetype['csv'],
        parquet_file=files_path_to_load_given_the_filetype['parquet'],
    )

    logging.info('Benchmarking data loaders...')
    # time how long it takes to load each dataframe from a file
    time_dataframe_loaders(
        files_path_to_load_given_the_filetype=files_path_to_load_given_the_filetype,
        progress_bar_enabled=True,
    )

    logging.info('Deleting mock data...')
    # delete the files
    os.remove(files_path_to_load_given_the_filetype['csv'])
    os.remove(files_path_to_load_given_the_filetype['parquet'])

    logging.info('Done.')


# %%
# Run program
if __name__ == '__main__':
    main()
