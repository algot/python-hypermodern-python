import tempfile

import nox

nox.options.sessions = "lint", "mypy", "pytype", "tests"

locations = "src", "tests", "noxfile.py"
versions = ["3.9", "3.10"]


@nox.session(python=versions)
def black(session):
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=versions)
def lint(session):
    args = session.posargs or locations
    install_with_constraints(session,
                             "flake8",
                             "flake8-bandit",
                             "flake8-black",
                             "flake8-bugbear",
                             "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=versions)
def tests(session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session(python=versions)
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python=versions)
def mypy(session):
    args = session.posargs or ["--ignore-missing-imports", *locations]
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=versions)
def pytype(session):
    """Run the static type checker."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


def install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
