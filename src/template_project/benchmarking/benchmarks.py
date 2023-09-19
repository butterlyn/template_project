# %%
# IMPORTING
# standard libary imports
from functools import partial
from typing import (
    Callable,
    Union,
    Type,
    Protocol,
    Any,
)
from types import ModuleType
# third party imports
import pandas as pd
import pyarrow.parquet as pq
import dask.dataframe as dd
import polars as pl
import fastparquet as fp
import duckdb
from duckdb import DuckDBPyConnection
# local imports
from utils import LoadersDictTypeHint


# %%
# LOADER BENCHMARKS

# Custom benchmarks

def fastparquet_parquet_return_as_dataframe_benchmark_function(file_path_to_load: str) -> None:
    """Benchmark function for loading a Parquet file into a dataframe using fastparquet"""
    fp.ParquetFile.to_pandas(
        fp.ParquetFile(file_path_to_load)
    )


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


class Benchmark(Protocol):
    benchmark_name: str
    benchmark_description: str
    benchmark_function: Union[Callable, Type]
    benchmark_units: str
    benchmark_library: str
    benchmark_results: Any


class LoaderBenchmark(Benchmark, Protocol):
    file_type: str
    benchmark_units: str = 'seconds'
    benchmark_results: float = None

    @property
    def file_path(self) -> str:
        return f'large_file.{self.file_type}'

    def benchmark(self, file_path: str = file_path) -> None:
        return self.benchmark_function(file_path)


class ComputeBenchmark(Benchmark, Protocol):
    input_data: Any
    benchmark_units: str = 'seconds'


class BenchmarkSuite(Protocol):
    benchmark_suite_name: str
    benchmark_suite_description: str
    benchmark_suite_benchmarks: list[Benchmark]


class LoaderBenchmarkSuite(BenchmarkSuite, Protocol):
    benchmark_suite_name: str
    benchmark_suite_description: str
    benchmark_suite_benchmarks: list[LoaderBenchmark]

    def benchmark_all(self, file_path: str = None) -> None:
        benchmark: LoaderBenchmark
        for benchmark in self.benchmark_suite_benchmarks:
            benchmark.benchmark(file_path=file_path)


class ComputeBenchmarkSuite(BenchmarkSuite, Protocol):
    benchmark_suite_name: str
    benchmark_suite_description: str
    benchmark_suite_benchmarks: list[ComputeBenchmark]


class Benchmarker(Protocol):
    benchmark_suite: BenchmarkSuite
    benchmark_suite_name: str
    benchmark_suite_description: str
    benchmark_suite_benchmarks: list[Benchmark]

    def benchmark_all(self) -> None:



# Compiled benchmarks

data_frame_loaders: LoadersDictTypeHint = {
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
