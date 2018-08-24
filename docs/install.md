
# Install the Chaos Hub

If you run the Chaos Hub locally (without Docker that is), either install the
Chaos Hub from a published release or build and install it from your local
clone.

## Install via Docker

As Chaos Hub requires some dependencies, it may be the easiest to fetch the
application via [Docker][docker].

[docker]: https://hub.docker.com/r/chaostoolkit/chaoshub/

Pull the image
```
$ docker pull chaostoolkit/chaoshub:0.1.2
```

## Install from a release

WARNING: No official releases have been made yet, so please install from a local
clone.

```
$ source  .venv/bin/activate
(.venv) $ pip install -U chaoshub
```

## Install from sources

First, build the UI:

```
$ cd ui
$ npm run build
```

Now, install the application in your Python virtual environment:

```
$ source  .venv/bin/activate
(.venv) $ cd app
(.venv) $ python setup.py install
(.venv) $ cd ..
```
