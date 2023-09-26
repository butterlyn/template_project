import nox


@nox.session
def cython_compile(session):
    session.install("cython", "numpy")
    session.run(
        "python",
        "nox_scripts/cython_compile.py",
        "build_ext",
        "--inplace",
    )


@nox.session
def type_check(session):
    session.install("mypy", "mypy-extensions")
    session.run("mypy", "--ignore-missing-imports", ".")


@nox.session
def lint(session):
    session.install("autopep8")
    session.run("autopep8", "--in-place", "--recursive", ".")


@nox.session
def test(session):
    session.install("pytest", "pytest-cov", "pytest-benchmark")
    session.install("-r", "requirements.txt")
    session.run("pytest", "tests")


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
