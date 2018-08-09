#!/usr/bin/env python
"""Chaos Hub chaoshubdashboard builder and installer"""
import io
import os
import sys

import setuptools


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
url = 'https://chaoshub.org'
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
    python_requires='>=3.7.*'
)


def main():
    """Package installation entry point."""
    setuptools.setup(**setup_params)


if __name__ == '__main__':
    main()