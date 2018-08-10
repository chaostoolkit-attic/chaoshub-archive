#!/usr/bin/env python
"""Chaos Hub Dashboard builder and installer"""
from distutils.errors import DistutilsFileError
import io
import os
import sys

import setuptools
import setuptools.command.build_py


def get_version_from_package() -> str:
    """
    Read the package version from the source without importing it.
    """
    path = os.path.join(
        os.path.dirname(__file__), "chaoshubdashboard/__init__.py")
    path = os.path.normpath(os.path.abspath(path))
    with open(path) as f:
        for line in f:
            if line.startswith("__version__"):
                token, version = line.split(" = ", 1)
                version = version.replace("'", "").strip()
                return version
    raise IOError("failed to locate chaoshubdashboard sources")


# since our ui assets live outside this package, we can't rely on any of the
# setuptools configuration settings to copy them. Let's do it manually.
# I'd rather not but this is what it is...
UI_ASSETS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "ui", "dist"))

class Builder(setuptools.command.build_py.build_py):
    def run(self):
        if not self.dry_run:
            ui_dir = os.path.join(self.build_lib, 'chaoshubdashboard/ui')
            if not os.path.isdir(UI_ASSETS_DIR):
                raise DistutilsFileError(
                    "Make sure you build the UI assets before creating this package")
            self.copy_tree(UI_ASSETS_DIR, ui_dir)
        setuptools.command.build_py.build_py.run(self)


name = 'chaoshub-dashboard'
desc = 'Chaos Hub Dashboard'

with io.open('README.md', encoding='utf-8') as strm:
    long_desc = strm.read()

classifiers = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: Implementation :: CPython'
]
author = 'ChaosIQ, Ltd'
author_email = 'contact@chaosiq.io'
url = 'https://github.com/chaostoolkit/chaoshub'
packages = [
    'chaoshubdashboard',
    'chaoshubdashboard.api',
    'chaoshubdashboard.api.services',
    'chaoshubdashboard.auth',
    'chaoshubdashboard.auth.services',
    'chaoshubdashboard.dashboard',
    'chaoshubdashboard.dashboard.services',
    'chaoshubdashboard.dashboard.views',
    'chaoshubdashboard.experiment',
    'chaoshubdashboard.experiment.services',
    'chaoshubdashboard.experiment.scheduler',
    'chaoshubdashboard.experiment.views'
]

setup_params = dict(
    cmdclass={
        'build_py': Builder,
    },
    name=name,
    version=get_version_from_package(),
    description=desc,
    long_description=long_desc,
    classifiers=classifiers,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    packages=packages,
    entry_points={
        'console_scripts': [
            'chaoshub-dashboard = chaoshubdashboard.__main__:cli'
        ],
        'chaoshub.scheduling': [
            'cron = chaoshubdashboard.experiment.scheduler.cron:CronScheduler',
            'local = chaoshubdashboard.experiment.scheduler.local:LocalScheduler'
        ]
    },
    include_package_data=True,
    python_requires='>=3.5.*'
)


def main():
    """Package installation entry point."""
    setuptools.setup(**setup_params)


if __name__ == '__main__':
    main()