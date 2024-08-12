import warnings

import aerospike
from flask import Flask, current_app

from flask_aerospike.session import (  # noqa: F401
    AerospikeSessionInterface,
    SessionDefaults,
)


class FlaskAerospike:
    """Main class used for initialization of Flask-Aerospike."""

    def __init__(self, app=None):
        # Flask related data
        self.app = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
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
        client = create_connections(self.config.get("FLASK_AEROSPIKE_CLIENT"))
        app.extensions["aerospike"][self] = {"conn": client}

        app.session_interface = self._get_interface(app, client)

    def _get_interface(self, app, client):
        config = app.config

        # Flask-session specific settings
        SESSION_PERMANENT = config.get(
            "SESSION_PERMANENT", SessionDefaults.SESSION_PERMANENT
        )
        SESSION_USE_SIGNER = config.get(
            "SESSION_USE_SIGNER", SessionDefaults.SESSION_USE_SIGNER
        )  # TODO: remove in 1.0
        SESSION_KEY_PREFIX = config.get(
            "SESSION_KEY_PREFIX", SessionDefaults.SESSION_KEY_PREFIX
        )
        SESSION_ID_LENGTH = config.get(
            "SESSION_ID_LENGTH", SessionDefaults.SESSION_ID_LENGTH
        )
        SESSION_SERIALIZATION_FORMAT = config.get(
            "SESSION_SERIALIZATION_FORMAT", SessionDefaults.SESSION_SERIALIZATION_FORMAT
        )

        # Aerospike settings
        SESSION_AEROSPIKE_NAMESPACE = config.get(
            "SESSION_AEROSPIKE_NAMESPACE", SessionDefaults.SESSION_AEROSPIKE_NAMESPACE
        )
        SESSION_AEROSPIKE_BIND_KEY = config.get(
            "SESSION_AEROSPIKE_BIND_KEY", SessionDefaults.SESSION_AEROSPIKE_BIND_KEY
        )

        common_params = {
            "app": app,
            "key_prefix": SESSION_KEY_PREFIX,
            "use_signer": SESSION_USE_SIGNER,
            "permanent": SESSION_PERMANENT,
            "sid_length": SESSION_ID_LENGTH,
            "serialization_format": SESSION_SERIALIZATION_FORMAT,
        }

        session_interface = AerospikeSessionInterface(
            **common_params,
            client=client,
            namespace=SESSION_AEROSPIKE_NAMESPACE,
            bind_key=SESSION_AEROSPIKE_BIND_KEY,
        )
        return session_interface

    @property
    def connection(self) -> aerospike.Client:
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
        client = aerospike.client({"hosts": [("127.0.0.1", 3000)]}).connect()

    return client
