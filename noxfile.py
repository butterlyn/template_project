# %%
# IMPORTS
# standard
from pathlib import Path
from typing import (
    Generator,
    Iterable,
    Callable,
)
import logging
import json
from functools import partial
# third party
import nox
from nox.sessions import Session
# %%
# CONFIGURATION

nox.options.sessions = []  # an empty list will display all sessions for command `nox`

ROOT_FILEPATH: str = str(Path.cwd())


# %%
# HELPER FUNCTIONS

def _get_conda_environment_relative_filepaths(root_filepath: str = str(Path.cwd())) -> list[str]:
    """Collect all conda environment*.yml filepaths relative to the root filepath of a project repository"""
    root_path: Path = Path(root_filepath)
    conda_environment_paths: Generator[Path, None, None] = root_path.glob(
        "environment*.yml",
    )
    path: Path
    conda_environment_relative_filepaths: list[str] = [
        str(path.relative_to(root_filepath))
        for path in conda_environment_paths
    ]
    return conda_environment_relative_filepaths


def _add_flags_to_cli_arugments(
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


def _check_if_julia_installed_in_nox_session(
    session: Session,
    conda_environment_name: str | None = None,
) -> bool:
    """Checks if julia or pyjulia is installed. Assumes nox session has a conda venv_backend."""
    # ~~~ resolve unset inputs ~~~
    conda_environment_name_reolved: str = (
        conda_environment_name if conda_environment_name is not None
        else Path(session.virtualenv.location).name
    )

    # ~~~ business logic ~~~
    conda_list_stout_json: dict = json.loads(
        session.run(  # type: ignore  # sesion.run returns a string, but mypy doesn't know that
            "conda",
            "run"
            "--name",
            conda_environment_name_reolved,
            "conda",
            "list",
            "--json",
            external=True,  # ensures nox session returns stdout as string
            silent=True,  # ensures nox session returns stdout as string
        )
    )
    installed_package_names: list[str] = [
        package_info["name"]
        for package_info
        in conda_list_stout_json["actions"]["LINK"]
    ]
    return (
        ("julia" in installed_package_names) or ("pyjulia" in installed_package_names)
    )


def _initialise_julia_in_nox_session(
    session: Session,
    conda_environment_name: str | None = None,
    _install_julia_script: str | None = None,
) -> None:
    """Initialise julia. Assumes nox session has a conda venv_backend."""
    # ~~~ resolve unset inputs ~~~
    conda_environment_name_resolved: str = (
        conda_environment_name if conda_environment_name is not None
        else Path(session.virtualenv.location).name
    )
    # helper function saved as a string to be run in python console, in case julia is not installed
    install_julia_script_resolved: str = (
        _install_julia_script if _install_julia_script is not None
        else (
            """
            import logging
            try:
                import julia
            except ImportError:
                logging.warning("Pyjulia not installed, skipping. Run `pip install julia` in python console.")
                break
            try:
                julia.install()
            except julia.JuliaError as error:
                logging.warning(
                    (
                        "Julia initialising failed, skipping. "
                        "Ensure Julia is installed and added to PATH then run `julia.install()` in python console."
                    ) + f"\\n{error}"
                )
            """
        )
    )
    # ~~~ business logic ~~~
    session.run(
        "conda",
        "run"
        "--name",
        conda_environment_name_resolved,
        "python",
        "-c",
        install_julia_script_resolved,
    )


# %%
# COMPOSABLE FUNCTIONS

# WIP. Not working yet. Can create new environment but doesn't align with environment.yml python version
# def production_conda_environment_in_nox_session(
#     session: Session,
#     create_new_environment: bool = False,
#     _ROOT_FILEPATH: str = ROOT_FILEPATH,
# ) -> None:
#     """
#     Set up production conda environment from environment*.yml files found in project repository within a nox session."""
#     # collect all conda environment files
#     conda_environment_relative_filepaths: list[str] = _get_conda_environment_relative_filepaths(
#         root_filepath=str(_ROOT_FILEPATH)
#     )
#     conda_install_environment_file_arugments: list[str] = _add_flags_to_cli_arugments(
#         cli_arugments=conda_environment_relative_filepaths,
#         flags="-f"
#     )

#     # ensure conda is updated
#     session.run(
#         "conda",
#         "update",
#         "--name",
#         "base",
#         "--channel",
#         "conda-forge",
#         "conda",
#         "--yes",
#     )

#     # conda environment from environment*.yml files
#     if create_new_environment:  # create new and activate
#         logging.debug("Creating new conda environment...")

#         # read conda json output to get new environment name
#         conda_stout_json_string: str = session.run(  # type: ignore  # sesion.run returns a string, but mypy doesn't know that
#             "conda",
#             "env",
#             "create",
#             *conda_install_environment_file_arugments,
#             "--json",
#             "--name",
#             "template_project_temp2",  # WIP TODO: make this come from environment.yml file
#             external=True,  # ensures nox session returns stdout as string
#             silent=True,  # ensures nox session returns stdout as string
#         )
#         conda_stout_json: dict = json.loads(conda_stout_json_string)
#         new_environment_name: str = Path(conda_stout_json["prefix"]).name

#         # check if julia is installed and initialise if so
#         if _check_if_julia_installed_in_nox_session(
#             session=session,
#             conda_environment_name=new_environment_name,
#         ):
#             _initialise_julia_in_nox_session(
#                 session=session,
#                 conda_environment_name=new_environment_name,
#             )

#         # activate the new environment
#         session.run(
#             "conda",
#             "activate",
#             new_environment_name,
#         )
#     else:
#         logging.debug("Updating conda environment...")
#         session.run(
#             "conda",
#             "env",
#             "update",
#             *conda_install_environment_file_arugments,
#             "--prune",
#             "--json",
#         )
#         # check if julia is installed and initialise if so
#         if _check_if_julia_installed_in_nox_session(
#             session=session,
#         ):
#             _initialise_julia_in_nox_session(
#                 session=session,
#             )


# create_new_production_conda_environment_in_nox_session: Callable = partial(
#     production_conda_environment_in_nox_session,
#     create_new_environment=True,
# )

# update_production_conda_environment_in_nox_session: Callable = partial(
#     production_conda_environment_in_nox_session,
#     create_new_environment=False,
# )


# %%
# NOX SESSIONS

# TODO: Make a 'setup' and 'run' sessions to setup and activate a conda environment, and run the program in that environment.
# --> `conda env list --json` to ensure the new conda environment name doesn't clash, `venv_backend="none"`
# --> https://nox.thea.codes/en/stable/cookbook.html


# # WIP not working yet. Can create new environment but doesn't align with environment.yml python version
# @nox.session(
#     venv_backend="none",
# )
# def set_up_env(session):
#     create_new_production_conda_environment_in_nox_session(session=session)


@nox.session
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


@nox.session
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


@nox.session
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

# # WIP
# @nox.session(
#     venv_backend="conda",
# )
# def test(session):
#     # Collect all conda environment files
#     update_production_conda_environment_in_nox_session(nox_session=session)

#     session.run(
#         "pip",
#         "install",
#         "pytest",
#         "pytest-cov",
#         "pytest-benchmark",
#     )
#     session.run(
#         "pytest",
#         "tests",
#     )


# TODO: add incremental typechecking, coverage, memory profiling, coverage, statistics, pyre configuration file
@nox.session
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
