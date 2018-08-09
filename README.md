# Home of the Chaos Hub Open-Source Project

![Chaos Hub][logo]

[logo]: https://github.com/chaostoolkit/chaoshub/raw/master/assets/chaoshub.png "Chaos Hub"

Welcome to the [Chaos Hub][hub], the Open Source dashboard for collaborative
Chaos Engineering. The project is sponsored by [ChaosIQ][chaosiq] and
licensed under the [AGPLv3+][agpl].

[hub]: https://chaoshub.org
[chaosiq]: https://chaosiq.io/
[agpl]: https://www.gnu.org/licenses/agpl-3.0.en.html

## Getting Chaos Hub up and running

This project is meant to be executed easily locally by default.

WARNING: Do not run a default, non-configured, instance on a public address.
This would be great honeypot!

### Using Docker

TBD

### From Sources

You can run the Chaos Hub locally without too much difficulties provided
you install the dependencies.

#### Python Requirements

The Chaos Hub is implemented in Python 3. It should support Python 3.5+ 
but has only been tested against Python 3.7.

Install Python for your system:

On MacOS X:

```
$ brew install python3
```

On Debian/Ubuntu:

```
$ sudo apt-get install python3 python3-venv
```

On CentOS:

```
$ sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
$ sudo yum -y install python35u
```

Notice, on CentOS, the Python 3.5 binary is named `python3.5` rather than
`python3` as other systems.

On Windows:

[Download the latest binary installer][pywin] from the Python website.

[pywin]: https://www.python.org/downloads/windows/

#### Dependencies

Dependencies can be installed for your system via its package management but,
more likely, you will want to install them yourself in a local virtual
environment.

```
$ python3 -m venv ~/.venvs/hub
```

Make sure to always activate your virtual environment before using it:

```
$ source  ~/.venvs/hub/bin/activate
(.venv) $
```

Once activated, install the dependencies as follows:

```
(.venv) $ pip install -r app/requirements.txt
```

### Launch the Chaos Hub

You can launch the Chaos Hub as follows:

```
(.venv) $ chaoshub-dashboard run --env-path app/.env --create-tables
```

By default, the Chaos Hub runs using an in-memory SQLite instance so you don't
have to configure it but it also means all your data will be lost everytime
you restart it.

You should read the [configuration][config] section to learn how to change that
behavior.

[config]: https://github.com/chaostoolkit/chaoshub/raw/master/docs/configure.md

## Use the Chaos Hub

Once started the Chaos Hub is a regular web application. Connect to it at
http://127.0.0.1:8080 by default and sign-up yourself.

## Contribute

Contributors to this project are welcome as this is an open-source effort that
seeks [discussions][join] and continuous improvement.

[join]: https://join.chaostoolkit.org/

From a code perspective, if you wish to contribute, you will need to run a 
Python 3.5+ environment. Then, fork this repository and submit a PR. The
project cares for code readability and checks the code style to match best
practices defined in [PEP8][pep8]. Please also make sure you provide tests
whenever you submit a PR so we keep the code reliable.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Hub project requires all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR. Also, we suggest you read our
take on the [license][] this project relies on to appreciate its rationale and
impact on your contributions.

[dco]: https://github.com/probot/dco#how-it-works
[license]: https://github.com/chaostoolkit/chaoshub/raw/master/docs/licensing.md
