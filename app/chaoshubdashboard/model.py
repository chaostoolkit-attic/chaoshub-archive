# -*- coding: utf-8 -*-
import os

from flask import current_app, Flask
from flask_sqlalchemy import SQLAlchemy as SA

__all__ = ["db", "get_user_info_secret_key", "get_db_conn_uri_from_env"]


class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        ssl_mode = app.config.get("sslmode", "allow")
        if ssl_mode != "allow":
            options["connect_args"] = {
                "sslmode": ssl_mode,
                "sslcert": app.config.get("ssl_client_cert"),
                "sslkey": app.config.get("ssl_key"),
                "sslrootcert": app.config.get("ssl_root_cert")
            }
        SA.apply_pool_defaults(self, app, options)


db = SQLAlchemy()


def get_db_conn_uri_from_env() -> str:
    """
    Create the DB connection URI to connect to the database backend.
    """
    host = os.getenv("DB_HOST", "")
    if host.startswith('sqlite:'):
        return host

    port = int(os.getenv("DB_PORT", 5432))
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PWD")
    name = os.getenv("DB_NAME")
    return "postgresql://{u}:{w}@{h}:{p}/{n}".format(
        u=user, w=pwd, h=host, p=port, n=name)


def get_user_info_secret_key() -> str:
    """
    Return the key used to encrypt/decrypt users details in our storage.
    """
    key = current_app.config.get("USER_PROFILE_SECRET_KEY")
    if not key:
        raise RuntimeError("User profile secret key not set!")
    return key
