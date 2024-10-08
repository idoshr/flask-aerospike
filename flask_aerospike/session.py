import warnings
from datetime import timedelta as TimeDelta
from typing import Optional

import aerospike
from aerospike import exception as ex
from flask import Flask
from flask_session._utils import total_seconds
from flask_session.base import ServerSideSession, ServerSideSessionInterface
from flask_session.defaults import Defaults


class SessionDefaults(Defaults):
    SESSION_AEROSPIKE = None
    SESSION_AEROSPIKE_NAMESPACE = "flask_sessions"
    SESSION_AEROSPIKE_BIND_KEY = "public"


class AerospikeSession(ServerSideSession):
    pass


class AerospikeSessionInterface(ServerSideSessionInterface):
    """Uses the Aerospike key-value store as a session storage. (`aerospike` required)

    :param client: A ``aerospike.Client`` instance.
    :param key_prefix: A prefix that is added to all storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.

    """

    session_class = AerospikeSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        client: Optional[aerospike.Client] = SessionDefaults.SESSION_AEROSPIKE,
        key_prefix: str = SessionDefaults.SESSION_KEY_PREFIX,
        use_signer: bool = SessionDefaults.SESSION_USE_SIGNER,
        permanent: bool = SessionDefaults.SESSION_PERMANENT,
        sid_length: int = SessionDefaults.SESSION_ID_LENGTH,
        serialization_format: str = SessionDefaults.SESSION_SERIALIZATION_FORMAT,
        namespace: str = SessionDefaults.SESSION_AEROSPIKE_NAMESPACE,
        bind_key: str = SessionDefaults.SESSION_AEROSPIKE_BIND_KEY,
    ):
        if client is None or not isinstance(client, aerospike.Client):
            warnings.warn(
                "No valid Aerospike instance provided, attempting to create a new instance on localhost with default settings.",
                RuntimeWarning,
                stacklevel=1,
            )
            self.client = aerospike.client({"hosts": [("127.0.0.1", 3000)]}).connect()
        else:
            self.client = client

        self.bind_key = bind_key
        self.namespace = namespace
        super().__init__(
            app, key_prefix, use_signer, permanent, sid_length, serialization_format
        )

    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (value) from the database
        try:
            serialized_session_data = self.client.get(
                (self.namespace, store_id, self.bind_key)
            )
        except (ex.RecordNotFound, ex.NamespaceNotFound):
            return None
        if serialized_session_data:
            return serialized_session_data[2]
        return None

    def _delete_session(self, store_id: str) -> None:
        try:
            self.client.remove((self.namespace, store_id, self.bind_key))
        except (ex.RecordNotFound, ex.NamespaceNotFound):
            pass

    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Update existing or create new session in the database

        self.client.put(
            key=(self.namespace, store_id, self.bind_key),
            bins=dict(session),
            meta={"ttl": storage_time_to_live},
        )
