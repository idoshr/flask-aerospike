import warnings

import aerospike
from flask import Flask, current_app

from flask_aerospike.session import *



class Aerospike:
    """Main class used for initialization of Flask-Aerospike."""

    def __init__(self, app=None):
        # Flask related data
        self.app = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app, client=None):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask application instance")

        self.app = app

        app.extensions = getattr(app, "extensions", {})

        if "aerospike" not in app.extensions:
            app.extensions["aerospike"] = {}

        if self in app.extensions["aerospike"]:
            # Raise an exception if extension already initialized as
            # potentially new configuration would not be loaded.
            raise ValueError("Extension already initialized")

        # Use app.config.
        self.config = app.config

        # Store objects in application instance so that multiple apps do not
        # end up accessing the same objects.
        s = {"conn": create_connections(client)}
        app.extensions["aerospike"][self] = s

    @property
    def connection(self) -> dict:
        """
        Return aerospike client associated with this aerospike
        instance.
        """
        return current_app.extensions["aerospike"][self]["conn"]


def create_connections(client: aerospike.Client):
    """
    Given Flask application's config dict, extract relevant config vars
    out of it and establish aerospike connection(s) based on them.
    """
    # Validate that the config is a dict and dict is not empty
    if client is None or not isinstance(client, aerospike.Client):
        warnings.warn(
            "No valid Aerospike instance provided, attempting to create a new instance on localhost with default settings.",
            RuntimeWarning,
            stacklevel=1,
        )
        client = aerospike.client({'hosts': [('127.0.0.1', 3000)]}).connect()

    return client
