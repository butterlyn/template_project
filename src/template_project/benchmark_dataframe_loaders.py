# standard libary imports
from collections.abc import MutableMapping
import os
import time
from functools import partial
from typing import (
    Any,
    Union,
    Callable,
    Type,
    TypeAlias,
    Protocol,
)
import logging
from typing import Iterable
from types import ModuleType
# third party imports
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import dask.dataframe as dd
import polars as pl
import fastparquet as fp
from alive_progress import alive_bar
from pydantic import (
    dataclasses,
    DataclassTypeError,
    BaseModel,
    Field,
    validator,
    ValidationError,
    root_validator,
    validate_arguments,
    validate_model,
    ConfigDict,
)
from rich.logging import RichHandler
from rich import traceback
import duckdb
from duckdb import DuckDBPyConnection


def getRichLogger(
    logging_level: str | int = "NOTSET",
    logger_name: str = __name__,
    enable_rich_logger: bool = True,
    rich_logger_format: str = "%(message)s",
    non_rich_logger_format: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    traceback_show_locals: bool = True,
    traceback_hide_dunder_locals: bool = True,
    traceback_hide_sunder_locals: bool = True,
    traceback_extra_lines: int = 10,
    traceback_suppressed_modules: Iterable[ModuleType] = (),
    additional_handlers: logging.Handler | Iterable[logging.Handler] | None = None,
) -> logging.Logger:
    """
    Substitute for logging.getLogger(), but pre-configured as rich logger with rich traceback.

    Parameters
    ----------
    logging_level : str or int, optional
        The logging level to use. Defaults to 'NOTSET'.
    logger_name : str, optional
        The name of the logger. Defaults to __name__.
    enable_rich_logger : bool, optional
        Whether to enable the rich logger and rich traceback or basic. Defaults to True.
    rich_logger_format : str, optional
        The format string to use for the rich logger. Defaults to "%(message)s".
    non_rich_logger_format : str, optional
        The format string to use for the non-rich logger. Defaults to "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s".
    traceback_show_locals : bool, optional
        Whether to show local variables in tracebacks. Defaults to True.
    traceback_hide_dunder_locals : bool, optional
        Whether to hide dunder variables in tracebacks. Defaults to True.
    traceback_hide_sunder_locals : bool, optional
        Whether to hide sunder variables in tracebacks. Defaults to True.
    traceback_extra_lines : int, optional
        The number of extra lines to show in tracebacks. Defaults to 10.
    traceback_suppressed_modules : Iterable[ModuleType], optional
        The modules to suppress in tracebacks (e.g., pandas). Defaults to ().
    additional_handlers : logging.Handler or list[logging.Handler], optional
        Additional logging handlers to use. Defaults to [].

    Returns
    -------
    logging.Logger
        The configured logger.

    Raises
    ------
    TypeError
        If additional_handlers is not a logging.Handler, Iterable[logging.Handler], or None.

    Example
    -------
    >>> import logging
    >>> from logger import getRichLogger
    >>> getRichLogger(loggin_level='DEBUG')
    >>> logging.debug("this is a rich debug message! the traceback of the below unhandled exception is also rich")
    >>> 1/0
    """

    # ~~~~~ helper functions ~~~~~

    def _install_rich_traceback() -> None:
        """Installs rich traceback for unhandled exceptions."""
        traceback.install(
            extra_lines=traceback_extra_lines,
            theme='monokai',
            show_locals=traceback_show_locals,
            locals_hide_dunder=traceback_hide_dunder_locals,
            locals_hide_sunder=traceback_hide_sunder_locals,
            suppress=traceback_suppressed_modules,
        )

    def _convert_additional_handlers_to_list() -> list[logging.Handler]:
        """Convert additional_handlers to list for combining with rich handler"""
        additional_handlers_list: list[logging.Handler] = (
            [additional_handlers] if isinstance(additional_handlers, logging.Handler)
            else list(additional_handlers) if isinstance(additional_handlers, Iterable)
            else [] if additional_handlers is None
            else TypeError(f"additional_handlers must be a logging.Handler, Iterable[logging.Handler], or None, not {type(additional_handlers)}")
        )
        return additional_handlers_list

    def _get_rich_handler() -> list[logging.Handler]:
        """Create rich handler in a list for combining with additional handlers"""
        return [
            RichHandler(
                level=logging.getLevelName(logging_level),
                omit_repeated_times=False,
                rich_tracebacks=enable_rich_logger,
                tracebacks_extra_lines=traceback_extra_lines,
                tracebacks_theme="monokai",
                tracebacks_word_wrap=False,
                tracebacks_show_locals=traceback_show_locals,
                tracebacks_suppress=traceback_suppressed_modules,
                log_time_format="[%Y-%m-%d %H:%M:%S] ",
            )
        ]

    # ~~~~~ business logic ~~~~~

    # Installs rich traceback for unhandled exceptions if enabled
    if enable_rich_logger:
        _install_rich_traceback()

    # Set the logger message format based on whether rich logger is enabled
    format: str = (
        rich_logger_format if enable_rich_logger
        else non_rich_logger_format
    )

    # Combine the rich handler with any additional handlers
    rich_handler = _get_rich_handler()
    additional_handlers_list = _convert_additional_handlers_to_list()
    all_handlers = (
        rich_handler + additional_handlers_list if enable_rich_logger
        else additional_handlers_list
    )

    # Configure the logger with the handlers
    logging.basicConfig(
        level=logging.getLevelName(logging_level),
        format=format,
        handlers=all_handlers,
    )

    # Get the logger and return it
    return logging.getLogger(logger_name)


getRichLogger(
    logging_level="INFO",
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)
logging.debug("Rich logger and rich traceback enabled")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# type hint for the dictionary of functions for loading dataframes from files
DataFrameLoaders: TypeAlias = dict[str, dict[str, dict[str, Union[Callable, Type]]]]
LoaderConfigDict: TypeAlias = ConfigDict[str, dict[str, dict[str, Union[Callable, Type]]]]


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


def flatten_dict(
    dictionary: MutableMapping,
    parent_key: str = '',
    sep: str = '.',
) -> dict[str, Any]:
    """Flatten a nested dictionary with a separator and return a new dictionary"""
    def _flatten_dict_gen(dictionary: MutableMapping, parent_key: str, sep: str):
        key: str
        value: Any
        for key, value in dictionary.items():
            new_key: str = parent_key + sep + key if parent_key else key
            if isinstance(value, MutableMapping):
                yield from flatten_dict(value, new_key, sep=sep).items()
            else:
                yield new_key, value
    return dict(_flatten_dict_gen(dictionary, parent_key, sep))


# def flatten_dict_deepest_pairs(dictionary: dict, max_level: int | None = None) -> list[Tuple[Any, Any]]:
#     result = []
#     for key, value in dictionary.items():
#         (
#             result.extend(flatten_dict_deepest_pairs(value, max_level - 1)) if isinstance(value, dict) and (max_level > 0 or max_level is None)
#             else result.append(tuple(key) + tuple(value))
#         )
#     return result


# fastparquet benchmark functions

def fastparquet_parquet_return_as_dataframe_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a Parquet file into a dataframe using fastparquet"""
    fp.ParquetFile.to_pandas(
        fp.ParquetFile(file_path_to_load)
    )


# duckdb benchmark functions

def duckdb_csv_basic_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a CSV file into a DuckDB database"""
    # Connect to the DuckDB database
    duckdb_memory_database: DuckDBPyConnection = duckdb.connect(database=':memory:')
    # Load the CSV file into a table using a SQL query
    duckdb_memory_database.execute(f"CREATE TABLE my_table AS SELECT * FROM read_csv_auto('{file_path_to_load}')")


def duckdb_csv_return_as_dataframe_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a CSV file into a DuckDB database and returning it as a pandas dataframe"""
    # Connect to the DuckDB database
    duckdb_memory_database: DuckDBPyConnection = duckdb.connect(database=':memory:')
    # Load the CSV file into a table using a SQL query
    duckdb_memory_database.execute(f"CREATE TABLE my_table AS SELECT * FROM read_csv_auto('{file_path_to_load}')")
    # Return the table as a dataframe
    duckdb_memory_database.execute("SELECT * FROM my_table").fetchdf()


def duckdb_parquet_basic_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a Parquet file into a DuckDB database"""
    # Connect to the DuckDB database
    duckdb_memory_database: DuckDBPyConnection = duckdb.connect(database=':memory:')
    # Load the parquet file into a table using a SQL query
    duckdb_memory_database.execute(f"CREATE TABLE my_table AS SELECT * FROM read_parquet('{file_path_to_load}')")


def duckdb_parquet_return_as_dataframe_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a Parquet file into a DuckDB database and returning it as a pandas dataframe"""
    # Connect to the DuckDB database
    duckdb_memory_database: DuckDBPyConnection = duckdb.connect(database=':memory:')
    # Load the parquet file into a table using a SQL query
    duckdb_memory_database.execute(f"CREATE TABLE my_table AS SELECT * FROM read_parquet('{file_path_to_load}')")
    # Return the table as a dataframe
    duckdb_memory_database.execute("SELECT * FROM my_table").fetchdf()


data_frame_loaders: DataFrameLoaders = {
    'csv': {
        'pandas': {
            'basic': pd.read_csv,
            'engine_pyarrow': partial(pd.read_csv, engine='pyarrow'),
            'engine_c': partial(pd.read_csv, engine='c'),
            'low_memory': partial(pd.read_csv, low_memory=True),
            'low_memory_engine_pyarrow': partial(pd.read_csv, low_memory=True, engine='pyarrow'),
            'low_memory_engine_c': partial(pd.read_csv, low_memory=True, engine='c'),
        },
        'dask': {
            'basic': dd.read_csv,
        },
        'polars': {
            'basic': pl.read_csv,
            'low_memory': partial(pl.read_csv, low_memory=True),
            'use_pyarrow': partial(pl.read_csv, use_pyarrow=True),
            'low_memory_use_pyarrow': partial(pl.read_csv, use_pyarrow=True, low_memory=True),
        },
        'duckdb': {
            'basic': duckdb_csv_basic_benchmark_function,
            'return_as_dataframe': duckdb_csv_return_as_dataframe_benchmark_function,
        }
    },
    'parquet': {
        'pandas': {
            'basic': pd.read_parquet,
            'engine_pyarrow': partial(pd.read_parquet, engine='pyarrow'),
            'engine_fastparquet': partial(pd.read_parquet, engine='fastparquet'),
        },
        'dask': {
            'basic': dd.read_parquet,
            'engine_pyarrow': partial(dd.read_parquet, engine='pyarrow'),
            'engine_fastparquet': partial(dd.read_parquet, engine='fastparquet'),
        },
        'polars': {
            'basic': pl.read_parquet,
            'use_pyarrow': partial(pl.read_parquet, use_pyarrow=True),
            'low_memory': partial(pl.read_parquet, low_memory=True),
            'low_memory_use_pyarrow': partial(pl.read_parquet, low_memory=True, use_pyarrow=True),
        },
        'duckdb': {
            'basic': duckdb_parquet_basic_benchmark_function,
            'return_as_dataframe': duckdb_parquet_return_as_dataframe_benchmark_function,
        },
        'fastparquet': {
            'basic (read only, no dataframe output)': fp.ParquetFile,
            'return_as_dataframe': fastparquet_parquet_return_as_dataframe_benchmark_function,
        },
        'pyarrow': {
            'basic (read only, no dataframe output)': pq.ParquetFile,
            'read_table (read only, no dataframe output)': pq.read_table,
        },
    },
}


# class DataFrameLoader(BaseModel):
#     data_frame_loaders: LoaderConfigDict = data_frame_loaders


def _time_how_long_to_load_dataframe(
    loader: Union[Callable, Type],
    file_path_to_load: str,
) -> float:
    """time how long it takes to load a dataframe from a file"""
    start_time: float = time.time()
    loader(file_path_to_load)
    end_time: float = time.time()
    return (end_time - start_time)


def _count_final_elements_in_dict(dictionary: dict) -> int:
    """count the number of final elements in a dictionary"""
    count: int = 0
    value: Any
    for value in dictionary.values():
        count += (
            _count_final_elements_in_dict(value) if isinstance(value, dict)
            else 1
        )
    return count


def time_dataframe_loaders(
    files_path_to_load_given_the_filetype: dict[str, str],
    progress_bar_enabled: bool = True,
) -> None:
    """time how long it takes to load a file using difference dataframe loaders"""
    # count the number of final elements in the dictionary load_dataframe_functions for the progress bar
    loader_count: int = _count_final_elements_in_dict(data_frame_loaders)

    with alive_bar(total=loader_count) if progress_bar_enabled else None as bar:
        # store the load time of each function
        load_times: dict[str, float] = dict()

        # time how long it takes to load each dataframe from a file
        file_type: str
        file_type_loaderss: dict[str, dict[str, Union[Callable, Type]]]
        library: str
        library_loaders_for_file_type: dict[str, Union[Callable, Type]]
        loader_name: str
        loader: Union[Callable, Type]
        for file_type, file_type_loaderss in data_frame_loaders.items():
            file_path_to_load = files_path_to_load_given_the_filetype[file_type]
            for library, library_loaders_for_file_type in file_type_loaderss.items():
                for loader_name, loader in library_loaders_for_file_type.items():
                    label: str = f'{file_type} {library} {loader_name}'
                    logging.debug(f'Loading {label}...')
                    load_time: float = _time_how_long_to_load_dataframe(
                        loader=loader,
                        file_path_to_load=file_path_to_load,
                    )
                    load_times[label] = load_time
                    bar()

    # sort by the load times, but only within the same library
    logging.debug('Sorting load times...')
    load_times_sorted: dict[str, float] = dict(  # sort by the load times
        sorted(
            load_times.items(),
            key=lambda item: item[1]
        )
    )

    # load_times_sorted: dict[str, float] = dict(  # then sort alphabetically by label
    #     sorted(
    #         load_times_sorted.items(),
    #         key=lambda item: item[0]
    #     )
    # )

    # Print the results to the console
    for label, load_time in load_times_sorted.items():
        print(f'\t{load_time:.4f} seconds {label}')


def main():
    files_path_to_load_given_the_filetype: dict[str, str] = {
        'parquet': 'large_file.parquet',
        'csv': 'large_file.csv',
    }

    logging.info('Generating mock data...')
    generate_data(
        num_rows=10000000,
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


if __name__ == '__main__':
    main()
