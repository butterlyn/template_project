import nox


@nox.session
def cython_compile(session):
    session.install("cython", "numpy")
    session.run(
        "python",
        "cython_compile.py",
        "build_ext",
        "--inplace",
    )


@nox.session
def type_check(session):
    session.install("mypy", "mypy-extensions")
    session.run("mypy", "--ignore-missing-imports", "src")


@nox.session
def lint(session):
    session.install("autopep8")
    session.run("autopep8", "--in-place", "--recursive", "src")


@nox.session
def test(session):
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest", "tests")

# # WIP not working yet 'refactor(test) add nox sess complexity'
# @nox.session
# def complexity(session):
#     session.install("wily")
#     session.run("wily", "build", "src/")
#     session.run("wily", "rank", "src/", "loc")
#     session.run("wily", "rank", "src/", "complexity")
#     session.run("wily", "rank", "src/", "mi")
#     session.run("wily", "report", "src/", "loc", "complexity", "mi")
