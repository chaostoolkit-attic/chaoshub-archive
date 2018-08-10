
# Install the Chaos Hub

If you run the Chaos Hub locally (without Docker that is), either install the
Chaos Hub from a published release or build and install it from your local
clone.

## Install from a release

WARNING: No official releases have been made yet, so please install from a local
clone.

```
$ source  .venv/bin/activate
(.venv) $ pip install -U chaoshub
```

## Install from sources

```
$ source  .venv/bin/activate
(.venv) $ cd app
(.venv) $ python setup.py install
(.venv) $ cd ..
```

## Install via Docker

TBD