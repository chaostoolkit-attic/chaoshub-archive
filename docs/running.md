# Launch the Chaos Hub

## Run with Docker

If you just want to try out the Chaos Hub, you may simply run it as a container:

```
$ docker run --rm -p 8080:8080 --name chaoshub -it chaostoolkit/chaoshub:0.1.2
```

Note that all data will be lost when the container exits.

## Run Locally

Ensure you have [setup][setup] your environment, and configured the settings,
before you can run the Chaos Hub.

[setup]: https://github.com/chaostoolkit/chaoshub/blob/master/docs/setup.md
[configure]: https://github.com/chaostoolkit/chaoshub/blob/master/docs/configure.md

Then launch the Chaos Hub as follows (using the default settings):

```
$ source  .venv/bin/activate
(.venv) $ chaoshub-dashboard run --env-path app/.env.sample --create-tables
```

By default, the Chaos Hub runs using an in-memory SQLite instance so you don't
have to configure it but it also means all your data will be lost everytime
you restart it.

You should read the [configuration][config] section to learn how to change that
behavior.

[config]: https://github.com/chaostoolkit/chaoshub/blob/master/docs/configure.md
