# %%
# IMPORTS
# standard libary imports
from typing import (
    Callable,
    Protocol,
)
import logging
# third party imports
from pydantic import (
    dataclasses,
    # DataclassTypeError,
    BaseModel,
    Field,
    validator,
    ValidationError,
    root_validator,
    validate_arguments,
    validate_model,
    # ConfigDict,
)
# local imports
from utils import LoadersDictTypeHint

# %%
# PROTOCOLS
class Benchmark(Protocol):
    benchmark_name: str
    benchmark_description: str
    benchmark_function: Union[Callable, Type]
    keyword_arguments: dict[str, Any]
    benchmark_units: str
    benchmark_library: str
    benchmark_results: Any

    def run_benchmark(self, input_data: Any) -> None:
        """Run the benchmark"""
        pass


class LoaderBenchmark(Benchmark, Protocol):
    file_type: str
    benchmark_units: str = 'seconds'
    benchmark_results: float = None

    @property
    def file_path(self) -> str:
        return f'large_file.{self.file_type}'

    def run_benchmark(self, file_path: str = file_path) -> None:
        pass


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
        pass

    def save_results(self) -> None:
        """Save the benchmark results to a file"""
        pass

# %%
# CLASSES

