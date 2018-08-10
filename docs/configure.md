# Configure the Chaos Hub

The Chaos Hub has only a few settings you can, and should, configure and they
all live inside the dotenv (`.env`) file you will be provided it at runtime.

A default set is provided [here][defaultdotenv]. You should copy it somewhere
and rename it to `.env`.

[defaultdotenv]: https://github.com/chaostoolkit/chaoshub/raw/master/app/.env.sample

Note that the configuration is never reloaded on the fly. You must restart
the process for changes to take effect.

## Database

By default, Chaos Hub relies on an in-memory SQLite instance. But, if you
want to persist state, you should rely on PostgreSQL instead.

To configure this, set the following keys in your .env:

```
DB_HOST="localhost"
DB_PORT=5432
DB_NAME="chaoshub"
DB_USER="chaoshub"
DB_PWD="secret"
```

A couple of notes:

* The database must be created manually. While Chaos Hub can create all the
  tables but not the database containing them.
* In the future, we will allow for better ways to TLS link to the database

## OAuth Providers

By default, Chaos Hub is configured so you can sign-up and sign-in using a
simple username/password scheme. However, you mays also configure OAuth2
providers to offload the authentication to them.

The following providers are supported out of the box: BitBucket, GitHub, GitLab
and Google. More will likely come.

To make them work, you need set their api/secret keys for each of the ones
you wish to use. Refer to their documentation to generate those keys.

The redirect uris to use are:

* BitBucket: http://<HOST>/auth/allowed/via/bitbucket
* GitHUb: http://<HOST>/auth/allowed/via/github
* GitLab: http://<HOST>/auth/allowed/via/gitlab
* Google: http://<HOST>/auth/allowed/via/google

Replace <HOST> by wherever you are hosting your instance. For example,
127.0.0.1:8080

## Secrets

You should set the `USER_PROFILE_SECRET_KEY` to a solid random
string which will be used to encrypt values in certain columns. Should you
lose this secret you would not be able to read said data. If you are breached,
you should change the key and encrypt all existing data.

Set `SIGNER_KEY` to a random string. It is used to sign all the JWT tokens.
If you change this value, all sessions will have to be refreshed by the users
by signing in again.

Set `SECRET_KEY` to a random string. It is used to sign the session itself.

Set `CLAIM_SIGNER_KEY` to a random string to sign all exchanged user claims
between the various services. If this changes while a claim is in traffic, it
will be rejected on the receiving and the call will have to be remade.
