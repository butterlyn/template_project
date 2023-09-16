import nox


@nox.session
def test(session):
    session.install("-r", "requirements_dev.txt")
    session.install("-r", "requirements.txt")
    session.run("autopep8", "--in-place", "--recursive", "src")
    session.run("pytest", "tests")
    session.run("pytest", "--cov", "src")
    session.run("mypy", "--ignore-missing-imports", "src")
    session.run("mprof", "run", "run.py")
    session.run("mprof", "plot", "--output", "mprof_plot.png")

# # WIP not working yet 'refactor(test) add nox sess complexity'
# @nox.session
# def complexity(session):
#     session.install("wily")
#     session.run("wily", "build", "src/")
#     session.run("wily", "rank", "src/", "loc")
#     session.run("wily", "rank", "src/", "complexity")
#     session.run("wily", "rank", "src/", "mi")
#     session.run("wily", "report", "src/", "loc", "complexity", "mi")
