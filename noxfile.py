import nox


@nox.session
def type_check(session):
    session.install("mypy")
    session.install("mypy-extensions")
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


@nox.session
def complexity(session):
    session.install("wily")
    session.run("wily", "build", "src/")
    session.run("wily", "report", "src/", "loc", "complexity", "mi")
    session.run("wily", "rank", "src/", "loc", "complexity", "mi")
