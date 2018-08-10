# ChaosHub

This repository contains the ChaosHub application and its various services.

## Overview

The ChaosHub app is a single process running the various services needed to
serve the application's features. Its design is a rather innane multi-tier
architecture. Basically, the application is backed by a relational database
and uses caching for performance.

However, the application is also designed to ease the split into standalone
microservices. Indeed, we have three main services in this application:

* auth: the Auth service provides basic user account operations such as
  creation based on OAuth with external services, token creations for the
  ChaosHub API itself
* dashboard: this is mainly the service to respond to the frontend needs
* experiment: this responds to the need for experiment management, both from
  the frontend and API perspective

While they live in the same process, they have been designed to support
separation of concerns as much as we could. Mainly, each talk to its own
database instance and thus their entities cannot link to one another through
relationalships.

Whenever one service needs data from another service, it uses an intermediary
function (usually living under their respective `services` directory). For now,
that function directly invokes the according function from the other service,
but should we split, this would be implemented to make a remote call
instead.

With that in mind, all the services endpoints take a `UserClaim` payload which
is encoded in a signed JWT token. That payload contains account information
such as the account id. This id is the key shared across all backend databases
to re-create the account's context. The payload also contains ChaosHub tokens
and the status of the account.

If we needed to turn one of the services into a standalone microservice, that
JWT token would still be transported equally well and allow for stateless
microservices.

Obviously, network links would induce latency and potential failures that should
be harnessed.

## Configuration

The application reads its configuration from dotenv files which contain key
and values for various bits and pieces such as the database connection details,
or the OAuth services keys.

When you run locally, a single .env file can be used, when running from
Kubernetes, it's a good idea to split the sources between config map and
secrets.

## Development

Working against the ChaosHub application is fairly simple but requires a bit
of setup. First, make sure you deploy a minikube cluster and use skaffold
so that everytime your code changes, the docker image of the application is
rebuilt and uploaded automatically into Kubernetes.

In regards to unit testing, you should be able to run them locally. As usual,
create a virtual environment for Python 3.6+ and install the dependencies
through the requirements files. Then, simply run `python setup.py develop` and
`pytest`.

Once we have automated build, those tests will be also executed continously.

The UI itself os developed in the `ui` repository.

```console
$ cd ../ui
$ npm run build
```

