# -*- coding: utf-8 -*-
import os.path

import cherrypy
from flask import Flask, session, url_for
from flask_caching import Cache
from requestlogger import WSGILogger
from werkzeug.contrib.fixers import ProxyFix

from chaoshubdashboard.app import serve_services
from chaoshubdashboard.settings import load_settings


def test_serve_blueprint():
    load_settings(os.path.join(os.path.dirname(__file__), ".env"))

    app = Flask(__name__)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    with app.app_context():
        serve_services(app, cache)

        assert "" in cherrypy.tree.apps
        wsgiapp = cherrypy.tree.apps[""]

        assert isinstance(wsgiapp, WSGILogger)

        wsgiapp = wsgiapp.application
        assert isinstance(wsgiapp, ProxyFix)
