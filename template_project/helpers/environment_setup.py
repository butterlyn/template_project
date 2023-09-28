# %%
# IMPORTS
# standard
from pathlib import Path
from typing import (
    Generator,
    Iterable,
)
import logging
import subprocess


# %%
# HELPER FUNCTIONS

def _get_conda_environment_relative_filepaths(root_filepath: str = str(Path.cwd())) -> list[str]:
    """Collect all conda environment*.yml filepaths relative to the root filepath of a project repository"""
    conda_environment_paths: Generator[Path, None, None] = Path.glob(
        Path(root_filepath),
        "environment*.yml",
    )
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


# helper function saved as a string to be run in python console, in case julia is not installed
_INSTALL_JULIA_SCRIPT: str = """
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
        ) + f"\n{error}"
    )
"""


# %%
# COMPOSABLE FUNCTIONS

def update_conda_environment_to_production_environment(
    enable_stdout_sterror: bool = True,
    root_filepath: str = str(Path.cwd()),
    _INSTALL_JULIA_SCRIPT: str = _INSTALL_JULIA_SCRIPT,
    _get_conda_environment_relative_filepaths: callable = _get_conda_environment_relative_filepaths,
    _add_flags_to_cli_arugments: callable = _add_flags_to_cli_arugments,
) -> int:
    """
    Update currently activated conda environment from environment*.yml files found in repo.
    Return code 0 indicates success.
    *WARNING*: This will uninstall any packages not listed in the environment*.yml files.
    """
    # collect all conda environment files
    conda_environment_relative_filepaths: list[str] = _get_conda_environment_relative_filepaths(
        root_filepath=str(root_filepath)
    )
    conda_install_environment_file_arugments: list[str] = _add_flags_to_cli_arugments(
        cli_arugments=conda_environment_relative_filepaths,
        flags="-f"
    )

    # update conda environment from environment*.yml files
    logging.debug("Updating conda environment...")
    subprocess_output: subprocess.CompletedProcess[str] = subprocess.run(
        ["conda", "env", "update", *conda_install_environment_file_arugments, "--prune"],
        check=True,
        capture_output=True,
        text=True,
    )

    # initialise julia if a julia conda environment is present
    logging.debug("Initialising julia...")
    for conda_environment_relative_filepath in conda_environment_relative_filepaths:
        if "julia" in Path(conda_environment_relative_filepath).name:
            subprocess.run(
                ["python", "-c", _INSTALL_JULIA_SCRIPT],
            )

    # print output if enabled
    if enable_stdout_sterror:
        print(subprocess_output.stdout)
        print(subprocess_output.stderr)

    return subprocess_output.returncode
