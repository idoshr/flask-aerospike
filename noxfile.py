"""Nox tool configuration file.

Nox is Tox tool replacement.
"""

import shutil
from pathlib import Path

import nox

nox.options.sessions = "latest", "lint", "documentation_tests"


def base_install(session, flask, aerospike):
    """Create basic environment setup for tests and linting."""
    session.run("python", "-m", "pip", "install", "--upgrade", "pip")
    session.run("python", "-m", "pip", "install", "setuptools_scm[toml]>=6.3.1")



    session.install(
        f"Flask{flask}",
        f"aerospike{aerospike}",
        f"flask-session",
    )
    return session


@nox.session(python="3.10")
def lint(session):
    """Run linting check locally."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a")


def _run_in_docker(session, db_version="5.0"):
    session.run(
        "docker",
        "run",
        "--name",
        "nox_docker_test",
        "-p 3000:3000 -p 3001:3001 -p 3002:3002",
        "-d",
        f"aerospike:{db_version}",
        external=True,
    )
    try:
        session.run("pytest", *session.posargs)
    finally:
        session.run_always("docker", "rm", "-fv", "nox_docker_test", external=True)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("flask", ["==1.1.4", "==2.0.3", "==2.3.3", ">=3.0.0"])
@nox.parametrize("aerospike", ["<15.0.0", ">=15.0.0"])
@nox.parametrize("db_version", ["ee-7.1.0.4"])
def full_tests(session, flask, aerospike, db_version):
    """Run tests locally with docker and complete support matrix."""
    session = base_install(session, flask, aerospike)
    _run_in_docker(session, db_version)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("db_version", ["ee-7.1.0.4"])
def latest(session, db_version):
    """Run minimum tests for checking minimum code quality."""
    flask = ">=3.0.0"
    aerospike = ">=15.0.0"
    session = base_install(session, flask, aerospike)
    if session.interactive:
        _run_in_docker(session, db_version)
    else:
        session.run("pytest", *session.posargs)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("flask", ["==1.1.4", "==2.0.3", "==2.3.3", ">=3.0.0"])
@nox.parametrize("aerospike", ["<15.0.0", ">=15.0.0"])
def ci_cd_tests(session, flask, aerospike):
    """Run test suite with pytest into ci_cd (no docker)."""
    session = base_install(session, flask, aerospike)
    session.run("pytest", *session.posargs)
