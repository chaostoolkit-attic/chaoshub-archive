# -*- coding: utf-8 -*-
import cherrypy
from cherrypy.process.plugins import Daemonizer, PIDFile
import click

from chaoshubdashboard import __version__
from chaoshubdashboard.app import create_app, cleanup_app
from chaoshubdashboard.settings import load_settings


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.option('--env-path', type=click.Path(),
              help='Dot env file or directory path.')
@click.option('--create-tables', is_flag=True,
              help='Create the database tables.')
def run(env_path: str, create_tables: bool = False):
    """
    Runs the chaoshub application.
    """
    load_settings(env_path)

    cherrypy.engine.subscribe(
        'start', lambda: create_app(
            create_tables=create_tables), priority=90)
    cherrypy.engine.subscribe('stop', cleanup_app, priority=30)
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
