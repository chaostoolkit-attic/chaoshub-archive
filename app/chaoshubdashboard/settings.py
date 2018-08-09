# -*- coding: utf-8 -*-
import glob
import logging
import logging.handlers
import os

import cherrypy
from dotenv import load_dotenv
from flask import Flask

__all__ = ["configure_app", "load_settings"]


def load_settings(env_path: str):
    """
    Load settings from the environment:

    * if `env_path` is a file, read it
    * if `env_path` is a directory, load, all its `*.env` files
    """
    if os.path.isdir(env_path):
        pattern = os.path.join(env_path, '**', '.env')
        for env_file in glob.iglob(pattern, recursive=True):
            cherrypy.log("Loading: {}".format(env_file))
            load_dotenv(dotenv_path=env_file)
    else:
        cherrypy.log("Loading: {}".format(env_path))
        load_dotenv(dotenv_path=env_path)

    debug = True if os.getenv('CHAOSHUB_DEBUG') else False
    cherrypy.config.update({
        'server.socket_host': os.getenv('SERVER_LISTEN_ADDR'),
        'server.socket_port': int(os.getenv('SERVER_LISTEN_PORT', 8080)),
        'engine.autoreload.on': False,
        'log.screen': debug,
        'log.access_file': '',
        'log.error_file': '',
        'environment': '' if debug else 'production',
        'tools.proxy.on': True,
        'tools.proxy.base': os.getenv('CHERRYPY_PROXY_BASE')
    })


def configure_app(app: Flask):
    """
    Configure the application from environmental variables. 
    """
    app.url_map.strict_slashes = False
    app.debug = True if os.getenv('CHAOSHUB_DEBUG') else False

    logger = logging.getLogger('flask.app')
    logger.propagate = False

    app.config["USER_PROFILE_SECRET_KEY"] = os.getenv(
        "USER_PROFILE_SECRET_KEY")
    app.config["SIGNER_KEY"] = os.getenv("SIGNER_KEY")
    app.config["CLAIM_SIGNER_KEY"] = os.getenv("CLAIM_SIGNER_KEY")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SESSION_COOKIE_DOMAIN"] = os.getenv("SESSION_COOKIE_DOMAIN")
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    app.config["GCE_PROJECT_ID"] = os.getenv("GCE_PROJECT_ID")
    app.config["GITHUB_CLIENT_ID"] = os.getenv("GITHUB_CLIENT_ID")
    app.config["GITHUB_CLIENT_SECRET"] = os.getenv("GITHUB_CLIENT_SECRET")
    app.config["GITLAB_CLIENT_ID"] = os.getenv("GITLAB_CLIENT_ID")
    app.config["GITLAB_CLIENT_SECRET"] = os.getenv("GITLAB_CLIENT_SECRET")
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
    app.config["BITBUCKET_CLIENT_ID"] = os.getenv("BITBUCKET_CLIENT_ID")
    app.config["BITBUCKET_CLIENT_SECRET"] = os.getenv(
        "BITBUCKET_CLIENT_SECRET")
    app.config["OAUTH_REDIRECT_BASE"] = os.getenv("OAUTH_REDIRECT_BASE", "/")

    app.secret_key = app.config["SECRET_KEY"]

    app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "simple")
    if app.config["CACHE_TYPE"] == "redis":
        app.config["CACHE_REDIS_HOST"] = os.getenv("CACHE_REDIS_HOST")
        app.config["CACHE_REDIS_PORT"] = os.getenv("CACHE_REDIS_PORT", 6379)

