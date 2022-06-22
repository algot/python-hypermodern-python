import tempfile
from typing import Any

import nox
from nox.sessions import Session

nox.options.sessions = "lint", "mypy", "pytype", "tests"

locations = "src", "tests", "noxfile.py"
versions = ["3.9", "3.10"]
package = "hypermodern_python"


@nox.session(python=versions)
def black(session: Session) -> None:
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=versions)
def lint(session: Session) -> None:
    args = session.posargs or locations
    install_with_constraints(session,
                             "flake8",
                             "flake8-annotations",
                             "flake8-bandit",
                             "flake8-black",
                             "flake8-bugbear",
                             "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=versions)
def tests(session: Session) -> None:
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session(python=versions)
def safety(session: Session) -> None:
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
def mypy(session: Session) -> None:
    args = session.posargs or ["--ignore-missing-imports", *locations]
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=versions)
def pytype(session: Session) -> None:
    """Run the static type checker."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype")
    session.run("pytype", *args)


@nox.session(python=versions)
def typeguard(session: Session) -> None:
    args = session.posargs or ["-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
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
