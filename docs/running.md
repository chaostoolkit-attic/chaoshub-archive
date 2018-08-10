# Launch the Chaos Hub

## Run Locally

Ensure you have [setup][setup] your environment before you can run the
Chaos Hub.

[setup]: https://github.com/chaostoolkit/chaoshub/blob/master/docs/setup.md

Then launch the Chaos Hub as follows:

```
$ source  .venv/bin/activate
(.venv) $ chaoshub-dashboard run --env-path app/.env --create-tables
```

By default, the Chaos Hub runs using an in-memory SQLite instance so you don't
have to configure it but it also means all your data will be lost everytime
you restart it.

You should read the [configuration][config] section to learn how to change that
behavior.

[config]: https://github.com/chaostoolkit/chaoshub/blob/master/docs/configure.md

## Run with Docker

TBD