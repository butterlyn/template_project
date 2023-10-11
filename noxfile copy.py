# %%
# IMPORTS
# standard library
from pathlib import Path
import shutil
import sys
# third party
import nox

# %%
# CONFIGURATION

# nox configuration options
NOX_DEFAULT_SESSIONS: list[str] = []  # specify which session to fun by default with command `nox`. An empty list will display all sessions instead of running any

# project configuration options
PYTHON_VERSIONS_TO_CYTHONIZE: str | list[str] = ["3.8", "3.9", "3.10", "3.11", "3.12"]
CONDA_ENVIRONMENT_NAME: str = "rtfs_for_forecasting"

# paths
SOURCE_CODE_DIRECTORY: str = "./src/rtfs_for_forecasting"
CYTHON_COMPILE_SCRIPT_FILEPATH: str = "./src/cython_compile.py"
CONDA_LOCK_FILEPATH: str = "./conda-lock.yml"
CONDA_ENVIRONMENT_YAML_FILEPATH: str = "./environment.yml"
TESTS_DIRECTORY: str = "./src/tests"
AEMO_PI_CONDA_PACKAGE_FILEPATH: str = "./aemo-pi-2.1-py310hb572761_1.tar.bz2"


# %%
# RESOLVE CONFIGURATION

def resolve_path(path: str) -> str:
    """Resolves a path to an absolute path compatible with the current operating system."""
    return str(Path(path).resolve())


source_code_directory: str = resolve_path(SOURCE_CODE_DIRECTORY)
cython_compile_script_filepath: str = resolve_path(CYTHON_COMPILE_SCRIPT_FILEPATH)
conda_lock_filepath: str = resolve_path(CONDA_LOCK_FILEPATH)
conda_environment_yaml_filepath: str = resolve_path(CONDA_ENVIRONMENT_YAML_FILEPATH)
tests_directory: str = resolve_path(TESTS_DIRECTORY)
aemo_pi_conda_package_filepath: str = resolve_path(AEMO_PI_CONDA_PACKAGE_FILEPATH)

# %%
# SET NOX OPTIONS

nox.options.sessions = NOX_DEFAULT_SESSIONS
nox.options.reuse_existing_virtualenvs = True  # False will recreate a fresh enviornment every time a session is run
nox.options.default_venv_backend = "conda"


# %%
# HELPER FUNCTIONS

def _update_conda_lock_files(session: nox.Session) -> None:
    """Updates the conda lock file. Must be run in a nox session with `venv_backend` set to conda."""
    session.run(
        "conda",
        "install",
        "conda-lock",
        "--channel", "conda-forge",
        "--yes",
    )
    session.run(
        "conda-lock",
        "lock",
        "--lockfile", conda_lock_filepath,
        "--file", conda_environment_yaml_filepath,
        "--kind", "env",
        "--kind", "lock",
        "--platform", "linux-64",
        "--platform", "win-64",
    )


# %%
# NOX SESSIONS

@nox.session
def setup_environment(session: nox.Session) -> None:
    """RUN THIS FIRST. Sets up the project conda environment. Must be run in a conda environment."""
    # update conda lock file
    _update_conda_lock_files(session)

    # create a conda environment from the conda lock file
    session.run(
        "conda-lock",
        "install", conda_lock_filepath,
        "--name", CONDA_ENVIRONMENT_NAME,
    )
    # install aemo-pi from a local file
    session.run(  # TODO: make a custom conda channel for aemo-pi
        "conda",
        "install",
        aemo_pi_conda_package_filepath,
        "--name", CONDA_ENVIRONMENT_NAME,
        "--yes",
    )
    session.log(f"conda environment setup complete. To activate the environment, run `conda activate {CONDA_ENVIRONMENT_NAME}`.")


@nox.session(python=PYTHON_VERSIONS_TO_CYTHONIZE, reuse_venv=False)
def compile_cython(session: nox.Session) -> None:
    """Compiles cython source code into python extension modules."""
    session.run(
        "conda",
        "install",
        "cython",
        "numpy",
        "--channel", "conda-forge",
        "--yes",
    )
    if sys.platform == "win32":
        session.run(
            "conda",
            "install",
            "pymsvc",
            "--channel", "conda-forge",
            "--yes",
        )
    # set the cwd to the cython compile script directory
    session.chdir(Path(cython_compile_script_filepath).parent)
    # compile the cython source code
    session.run("python", cython_compile_script_filepath, "build_ext", "--inplace")
    # delete the build directory
    shutil.rmtree(Path("./build"))


@nox.session(venv_backend='virtualenv')
def type_check(session: nox.Session) -> None:
    "Runs static type checking on project source code."
    session.run(
        "pip",
        "install",
        "mypy",
        "mypy_extensions",
    )
    session.run("mypy", "--ignore-missing-imports", source_code_directory)


@nox.session
def update_conda_lock_files(session: nox.Session) -> None:
    """Updates the conda lock file."""
    _update_conda_lock_files(session)


@nox.session(
    venv_backend='none'  # run tests in the current environment instead of creating a fresh virtual environment for the session
)
def test(session: nox.Session) -> None:  # TODO: make this run on a fresh virtual environment environment
    """Runs tests, coverage, and benchmarks."""

    session.run(
        "pip",
        "install",
        "pytest",
        "pytest-cov",
        "pytest-benchmark",
    )
    session.run(
        "pytest",
        tests_directory,
    )
