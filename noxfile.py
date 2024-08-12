"""Nox tool configuration file.

Nox is Tox tool replacement.
"""

import nox

nox.options.sessions = "latest", "lint", "documentation_tests"


def base_install(session, flask, aerospike, flask_session):
    """Create basic environment setup for tests and linting."""
    session.run("python", "-m", "pip", "install", "--upgrade", "pip")
    session.run("python", "-m", "pip", "install", "setuptools_scm[toml]>=6.3.1")

    session.install(
        f"Flask{flask}",
        f"aerospike{aerospike}",
        f"flask-session{flask_session}",
        "-e",
        ".[dev]",
    )
    return session


@nox.session(python="3.10")
def lint(session):
    """Run linting check locally."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a")


def _run_in_docker(session, db_version="7.0"):
    session.run(
        "docker",
        "run",
        "--name",
        "nox_docker_test",
        "-p",
        "3000:3000",
        "-d",
        f"aerospike/aerospike-server:{db_version}",
        external=True,
    )
    try:
        session.run("pytest", *session.posargs)
    finally:
        session.run_always("docker", "rm", "-fv", "nox_docker_test", external=True)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("flask", ["==2.3.3", ">=3.0.0"])
@nox.parametrize("aerospike", ["<15.0.0", ">=15.0.0"])
@nox.parametrize("flask_session", ["==0.8.0"])
@nox.parametrize("db_version", ["6.4", "7.0", "7.1"])
def full_tests(session, flask, aerospike, db_version, flask_session):
    """Run tests locally with docker and complete support matrix."""
    session = base_install(session, flask, aerospike, flask_session)
    _run_in_docker(session, db_version)


@nox.session(python=["3.11"])
def latest(session):
    """Run minimum tests for checking minimum code quality."""
    db_version = "7.1"
    flask = ">=3.0.0"
    aerospike = ">=15.0.0"
    flask_session = ">=0.8.0"
    session = base_install(session, flask, aerospike, flask_session)
    if session.interactive:
        _run_in_docker(session, db_version)
    else:
        session.run("pytest", *session.posargs)


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
@nox.parametrize("flask", ["==2.3.3", ">=3.0.0"])
@nox.parametrize("flask_session", ["==0.8.0"])
@nox.parametrize("aerospike", ["<15.0.0", ">=15.0.0"])
def ci_cd_tests(session, flask, aerospike, flask_session):
    """Run test suite with pytest into ci_cd (no docker)."""
    session = base_install(session, flask, aerospike, flask_session)
    session.run("pytest", *session.posargs)
