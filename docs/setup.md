# Setup your Environment

The Chaos Hub open source project was designed to be executed locally, with
 minimal requirements, by default.

> **WARNING**: It is _not_ recommended run a default, non-configured, instance
 on a public address.

To run the Chaos Hub locally you need to install the following dependencies
 first.

## Application Python Requirements

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

## Dependencies

Chaos Hub dependencies can be installed for your system via its package 
management system but, more likely, you may want to install them yourself in a local python virtual environment using:

```
$ python3 -m venv .venv
```

Make sure to **always** activate your virtual environment before using it:

```
$ source  .venv/bin/activate
(.venv) $
```

Once activated you can install the Chaos Hub dependencies using:

```
(.venv) $ pip install -r app/requirements.txt
```

## UI TypeScript dependencies

To create and work with the UI elements for the Chaos Hub you need to install
 [npm][npm] on your machine and then install the required dependencies:

[npm]: https://www.npmjs.com/

```
$ cd ui
$ npm -g install poi
$ npm install
```

> **NOTE**: You may need to use `sudo` to install global npm dependencies.
