# %%
# IMPORTS
# standard
from pathlib import Path
from typing import (
    TypedDict,
    Callable,
    Any,
)
from typing_extensions import (
    LiteralString,
)
from functools import (
    partial,
)
import logging
# third-party
import polars as pl
from icecream import ic
# local
from helpers.rich_logger import getRichLogger

# %%
# LOGGER
logger: logging.Logger = getRichLogger(
    logging_level="DEBUG",
    logger_name=__name__,
    traceback_show_locals=True,
    traceback_extra_lines=10,
    traceback_suppressed_modules=(),
)


# %%
# NODES, PIPES, PIPELINES, PIPELINE_NETWORKS

def pipe_intermediate_processing(lf: pl.LazyFrame) -> pl.LazyFrame:
    return (
        lf
        .cast(
            {
                "identifier": pl.Utf8,
                "content": pl.Utf8,
                "position_in_document": pl.UInt16,
                "level": pl.UInt8,
            }
        )
        .with_columns(
            pl.col("wem_rules_publication_iso_date").str.strptime(dtype=pl.Date, format="%Y-%m-%d").alias("wem_rules_publication_date"),
        )
        .drop("wem_rules_publication_iso_date")
    )


def pipeline_process_wem_rules_clauses(
    # inputs
    lf: pl.LazyFrame,
    # configuration
    # parameters
) -> pl.LazyFrame:
    return (
        lf
        .pipe(
            pipe_intermediate_processing,
        )
    )


def pipeline_iterations(
    lf: pl.LazyFrame,
    iterations: int = 1,
):
    for _ in range(iterations):
        lf = (
            lf
            .pipe(pipeline_process_wem_rules_clauses)
        )
    return lf

# %%
# IO STRATEGIES


def scan_ndjson_to_lazyframe(source: LiteralString, **load_kwargs) -> pl.LazyFrame:
    logger.info("Loading ndjson to lazyframe...")
    return (
        pl.scan_ndjson(
            source,
            **load_kwargs,
        )
    )


def read_ndjson_to_lazyframe(source: LiteralString, **load_kwargs) -> pl.LazyFrame:
    logger.info("Loading ndjson to lazyframe...")
    return (
        pl.read_ndjson(
            source,
            **load_kwargs,
        )
    )


# %%
# DATA CATALOG
# define raw data sources

raw_data: dict[str, pl.LazyFrame] = {
    "scanned_raw_wem_rules_clauses": scan_ndjson_to_lazyframe(
        source=Path(r"template_project/wem_rules_clauses.ndjson").resolve().as_posix(),
        infer_schema_length=10,
        low_memory=False,
        n_rows=None,
    ),
    "read_raw_wem_rules_clauses": read_ndjson_to_lazyframe(
        source=Path(r"template_project/wem_rules_clauses.ndjson").resolve().as_posix(),
    ),
}


# %%
# OUTPUT STRATEGIES

def profile_collect_strategies(lf: pl.LazyFrame) -> None:
    try:
        no_optimisation_microsecond_runtime: int | None = lf.profile(no_optimization=True)[1].select(pl.col("end").last())[0, 0]
    except MemoryError:
        logger.warning("No optimisation profile failed")
        no_optimisation_microsecond_runtime = None
    try:
        optimised_microsecond_runtime: int | None = lf.profile()[1].select(pl.col("end").last())[0, 0]
    except MemoryError:
        logger.warning("Optimised profile failed")
        optimised_microsecond_runtime = None
    try:
        streaming_optimised_microsecond_runtime: int | None = lf.profile(streaming=True)[1].select(pl.col("end").last())[0, 0]
    except MemoryError:
        logger.warning("Streaming optimised profile failed")
        streaming_optimised_microsecond_runtime = None

    profiling_results: pl.DataFrame = pl.DataFrame(
        {
            "collect_strategy": ["no_optimisation", "optimised", "streaming_optimised"],
            "runtime_microseconds": [
                no_optimisation_microsecond_runtime,
                optimised_microsecond_runtime,
                streaming_optimised_microsecond_runtime],
        }
    )
    ranked_profiling_results: pl.DataFrame = (
        profiling_results
        .with_columns(
            pl.col("runtime_microseconds").truediv(1_000).alias("runtime_milliseconds"),
        )
        .drop("runtime_microseconds")
        .sort("runtime_milliseconds")
    )
    ic(ranked_profiling_results)


def profile_streaming(lf: pl.LazyFrame) -> None:
    try:
        streaming_optimised_microsecond_runtime: int | None = lf.profile(streaming=True)[1].select(pl.col("end").last())[0, 0]
    except RuntimeError:
        logger.warning("Streaming optimised profile failed")
        streaming_optimised_microsecond_runtime = None

    profiling_results: pl.DataFrame = pl.DataFrame(
        {
            "collect_strategy": ["streaming_optimised"],
            "runtime_microseconds": [streaming_optimised_microsecond_runtime],
        }
    )
    ranked_profiling_results: pl.DataFrame = (
        profiling_results
        .with_columns(
            pl.col("runtime_microseconds").truediv(1_000).alias("runtime_milliseconds"),
            pl.col("runtime_microseconds").truediv(1_000_000).alias("runtime_seconds"),
        )
        .drop("runtime_microseconds")
    )
    ic(ranked_profiling_results)


def collect_and_print_lazyframe(lf: pl.LazyFrame) -> None:
    ic(lf.collect().head(10))


def print_lazyframe_as_dict(lf: pl.LazyFrame) -> None:
    ic(lf.collect().to_dict())


def describe_lazyframe(lf: pl.LazyFrame) -> None:
    ic(lf.collect(streaming=True).describe())


def show_graphs(lf: pl.LazyFrame) -> None:
    ic(lf.show_graph(streaming=True, optimized=True))
    ic(lf.show_graph(streaming=True, optimized=False))


def pipe_test_identifier_regex(lf: pl.LazyFrame) -> pl.LazyFrame:
    identifiers_not_included_in_regex: pl.LazyFrame = (
        lf
        .with_columns(
            pl.col("identifier").str.contains(r"^<insert_regex_here>$").alias("regex_match_level_1"),
            pl.col("identifier").str.contains(r"^<insert_regex_here>$").alias("regex_match_level_2"),
            pl.col("identifier").str.contains(r"(^[1-9]\.[1-9][0-9]?[A-Z]{0,2}.[1-9][0-9]?([A-D])?\.?\s{0,3}$)|(^Step\s?[0-9]{0,2}[A-Z]?\:\s?$)").alias("regex_match_level_3"),
            pl.col("identifier").str.contains(r"\([a-zI][A-Z]?\).*$").alias("regex_match_level_4"),
            pl.col("identifier").str.contains(r"^(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})([A-D])?\.?\s*$").alias("regex_match_level_5"),
        )
        .filter(
            ((pl.col("level") == 1) & ~(pl.col("regex_match_level_1"))) |
            ((pl.col("level") == 2) & ~(pl.col("regex_match_level_2"))) |
            ((pl.col("level") == 3) & ~(pl.col("regex_match_level_3"))) |
            ((pl.col("level") == 4) & ~(pl.col("regex_match_level_4"))) |
            ((pl.col("level") == 5) & ~(pl.col("regex_match_level_5")))
        )
        .select(
            pl.col("identifier"),
            pl.col("level"),
        )
        .group_by(pl.col("level"))
        .agg(pl.col("identifier").count().alias("identifiers_remaining"))
        .collect(streaming=True)
    )
    return ic(identifiers_not_included_in_regex)


output_strategies: dict[str, Callable[[pl.LazyFrame], None]] = {
    "profile_collect_strategies": profile_collect_strategies,
    "profile_streaming": profile_streaming,
    "collect_and_print_lazyframe": collect_and_print_lazyframe,
    "describe_lazyframe": describe_lazyframe,
    "print_lazyframe_as_dict": print_lazyframe_as_dict,
    "pipe_test_identifier_regex": pipe_test_identifier_regex,
    "show_graphs": show_graphs,
}


# %%
# PIPELINE RUNNER

class RunQueueItem(TypedDict):
    run_name: str
    pipeline: Callable
    inputs: dict[str, pl.LazyFrame]
    parameters: dict[str, Any]
    output_strategy: Callable[[pl.LazyFrame], None]


def run_pipelines(run_queue: list[RunQueueItem]) -> None:

    # instantiate run queue
    output_executeables_queue: list[Callable[[], None]] = list()
    run_queue_item: RunQueueItem
    for run_queue_item in run_queue:
        create_execution_plans: Callable[[], Any] = partial(
            run_queue_item["pipeline"],
            **run_queue_item["inputs"],
            **run_queue_item["parameters"],
        )

        output_executable: Callable[[], None] = partial(run_queue_item["output_strategy"], create_execution_plans())
        output_executeables_queue.append(output_executable)

    # execute run queue
    output_executeable: Callable[[], None]
    execution_index: int
    for execution_index, output_executeable in enumerate(output_executeables_queue):
        logger.info(f"Running pipeline {execution_index + 1} of {len(output_executeables_queue)}")
        output_executeable()


# %%
# RUN PIPELINES

if __name__ == "__main__":
    ic.disable()
    # configure run queue
    run_queue: list[RunQueueItem] = [
        {
            "run_name": "process_wem_rules_clauses_run_1",
            "pipeline": pipeline_process_wem_rules_clauses,
            "inputs": {
                "lf": raw_data["scanned_raw_wem_rules_clauses"]
            },
            "parameters": {},
            "output_strategy": output_strategies["collect_and_print_lazyframe"]
        },
        {
            "run_name": "process_wem_rules_clauses_run_2",
            "pipeline": pipeline_process_wem_rules_clauses,
            "inputs": {
                "lf": raw_data["scanned_raw_wem_rules_clauses"]
            },
            "parameters": {},
            "output_strategy": output_strategies["profile_collect_strategies"]
        },
        {
            "run_name": "process_wem_rules_clauses_run_2",
            "pipeline": pipeline_process_wem_rules_clauses,
            "inputs": {
                "lf": raw_data["scanned_raw_wem_rules_clauses"]
            },
            "parameters": {},
            "output_strategy": output_strategies["describe_lazyframe"]
        },
        {
            "run_name": "process_wem_rules_clauses_run_2",
            "pipeline": pipeline_process_wem_rules_clauses,
            "inputs": {
                "lf": raw_data["scanned_raw_wem_rules_clauses"]
            },
            "parameters": {},
            "output_strategy": output_strategies["pipe_test_identifier_regex"]
        },
    ]

    run_pipelines(run_queue=run_queue)

    # output_strategies["collect_and_print_lazyframe"](
    #     pipeline_process_wem_rules_clauses(
    #         raw_data["raw_wem_rules_clauses"]
    #     )
    # )

    # from kedro.pipeline import pipeline, node, Pipeline
    # from kedro.runner.sequential_runner import SequentialRunner
    # from kedro.runner import AbstractRunner

    # runner: type[AbstractRunner] = SequentialRunner

    # runner.run(
    #     pipeline=pipeline(
    #         [
    #             node(
    #                 func=output_strategies["collect_and_print_lazyframe"](pipeline_process_wem_rules_clauses(raw_data["raw_wem_rules_clauses"])),
    #                 inputs=None,
    #                 outputs=None,
    #                 name="profile_collect_strategies",
    #             ),
    #         ]
    #     ),
    #     catalog=None,
    # )
