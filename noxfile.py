# %%
# IMPORTS
# standard
from pathlib import Path
from typing import (
    Generator,
    Iterable,
)
# third party
import nox

# %%
# CONFIGURATION

nox.options.sessions = []  # an empty list will display all sessions for command `nox`

PYTHON_VERSIONS: str | list[str] = "3.10"


# %%
# FUNCTIONS

def get_conda_environment_relative_filepaths(root_filepath: str = str(Path.cwd())) -> list[str]:
    """Collect all conda environment*.yml filepaths relative to the root filepath of a project repository"""
    conda_environment_paths: Generator[Path, None, None] = Path.glob(Path(root_filepath), "environment*.yml")
    conda_environment_relative_filepaths: list[str] = [str(path.relative_to(root_filepath)) for path in conda_environment_paths]
    return conda_environment_relative_filepaths


def add_flags_to_cli_arugments(
    cli_arugments: list[str],
    flags: str | Iterable[str],
) -> list[str]:
    """
    Adds flag to a list of command line interface (cli) arugments to prepare them to be passed to the command line.
    e.g.:
    >>> add_flag_to_flag_arumgnets(["environment.yml", "environment-dev.yml"], "-f")  # output: ["-f", "environment.yml", "-f", "environment-dev.yml"]
    >>> subprocess("conda", "env", "update", *["-f", "environment.yml", "-f", "environment-dev.yml"], "--prune")  # update conda environment from environment.yml and environment-dev.yml
    """
    # resolve inputs
    flags_list: list[str]
    if isinstance(flags, Iterable):
        flags_list = list(flags)  # convert to list if not already
    if isinstance(flags, str):
        flags_list = [flags] * len(cli_arugments)
    # check inputs are valid
    if len(flags_list) != len(cli_arugments):
        raise ValueError(f"Length of flags ({len(flags_list)}) must match length of flag_arugments ({len(cli_arugments)})")
    # add flags to flag_arugments
    cli_arguments_with_flags: list[str] = []
    for flag, argument in zip(flags_list, cli_arugments):
        cli_arguments_with_flags.extend([flag, argument])
    return cli_arguments_with_flags


# %%
# NOX SESSIONS

# TODO: Make a 'setup' and 'run' sessions to setup and activate a conda environment, and run the program in that environment.
# --> `conda env list --json` to ensure the new conda environment name doesn't clash, `venv_backend="none"`
# --> https://nox.thea.codes/en/stable/cookbook.html

@nox.session(python=PYTHON_VERSIONS)
def cython_compile(session):
    session.run(
        "pip",
        "install",
        "cython",
        "numpy",
    )
    session.run(
        "python",
        "cython_compile.py",
        "build_ext",
        "--inplace",
    )


@nox.session(python=PYTHON_VERSIONS)
def type_check(session):
    session.run(
        "pip",
        "install",
        "mypy",
        "mypy-extensions",
    )
    session.run(
        "mypy",
        "--ignore-missing-imports",
        ".",
    )


@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    session.run(
        "pip",
        "install",
        "autopep8",
    )
    session.run(
        "autopep8",
        "--in-place",
        "--recursive",
        ".",
    )


@nox.session(
    venv_backend="conda",
    python=PYTHON_VERSIONS,
)
def test(session):
    # Collect all conda environment files
    conda_environment_relative_filepaths: list[str] = get_conda_environment_relative_filepaths(root_filepath=str(Path.cwd()))
    conda_install_environment_file_arugments: list[str] = add_flags_to_cli_arugments(
        cli_arugments=conda_environment_relative_filepaths,
        flags="-f"
    )

    session.run(
        "conda",
        "env",
        "update",
        *conda_install_environment_file_arugments,
        "--prune",
    )
    session.run(
        "pip",
        "install",
        "pytest",
        "pytest-cov",
        "pytest-benchmark",
    )
    session.run(
        "pytest",
        "tests",
    )


# TODO: add incremental typechecking, coverage, memory profiling, coverage, statistics, pyre configuration file
@nox.session(python=PYTHON_VERSIONS)
def pyre(session):
    session.run(
        "pip",
        "install",
        "pyre-check",
    )
    session.run(
        "pyre",
        "--source-directory",
        ".",
        "check",
    )

# # WIP not working yet. add automatic appending of @profile for functions
# @nox.session
# def profile_memory(session):
#     session.install("memory_profiler")
#     session.run("python", "-m", "memory_profiler", "run.py")
#     session.run("mprof", "run", "python", "run.py")
#     session.run("mprof", "plot")
#     session.run("mprof", "clean")

# # WIP not working yet 'refactor(test) add nox sess complexity'
# @nox.session
# def complexity(session):
#     session.install("wily")
#     session.run("wily", "build", "src/")
#     session.run("wily", "rank", "src/", "loc")
#     session.run("wily", "rank", "src/", "complexity")
#     session.run("wily", "rank", "src/", "mi")
#     session.run("wily", "report", "src/", "loc", "complexity", "mi")

# TODO: memory_profiler  # WIP
# TODO: pycallgraph2  # requires graphviz installation
# TODO: willy  # WIP
# TODO: py-heat  # requires conda install
# TODO: pyan3
# TODO: cProfile + snakeviz
# TODO: pyinstrument
# TODO: flamegraphs https://pythonspeed.com/articles/a-better-flamegraph/
# TODO: eliot (@log_call) + eliottree
# TODO: Mccabe
# TODO: sciagraph https://www.sciagraph.com/

# TODO: pyre

# TODO: plantuml (a) from Kedro (b) from dagster (b) from custom
# TODO: run python-docx-template
# TODO: generate obsidian docs application from mkdocs

# TODO: sphinx/mkdocs

# TODO: package application with conda constructor/nuitka/pyinstaller
# TODO: build with .toml/setup.py and run everything (no environment setup required)
# TODO: create docker image from dockerfile
# TODO: install and initialise julia

# TODO: run dagster local
# TODO: run dagster cloud (set the working directory to dagster HOME through environment variable DAGSTER_HOME)
# TODO: dagster materialize all
# TODO: run kedro
# TODO: kedro viz

# TODO: pull dagster starter
# TODO: pull kedro starter
# TODO: generate conda local channel
