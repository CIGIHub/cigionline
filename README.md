# cigionline

[![Django CI](https://github.com/CIGIHub/cigionline/workflows/Django%20CI/badge.svg)](https://github.com/CIGIHub/cigionline/actions?query=workflow%3A%22Django+CI%22)
[![Node.js CI](https://github.com/CIGIHub/cigionline/workflows/Node.js%20CI/badge.svg)](https://github.com/CIGIHub/cigionline/actions?query=workflow%3A%22Node.js+CI%22)
[![Coverage Status](https://coveralls.io/repos/github/CIGIHub/cigionline/badge.svg)](https://coveralls.io/github/CIGIHub/cigionline)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=CIGIHub/cigionline)](https://dependabot.com)

Wagtail source code for cigionline.org


## Installation
This project uses Python 3.12.4.
``` shell
$ git clone git@github.com:CIGIHub/cigionline.git
$ cd cigionline
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### PostgreSQL
We use PostgreSQL for our database. Once you have PostgreSQL [installed](https://postgresapp.com), run the following commands to set up your local database.
``` shell
$ create user cigi password 'cigi' superuser
$ create database cigionline
```

If you have a copy of the database file, it can be imported with the following command:
``` shell
$ pg_restore --verbose --clean --no-acl --no-owner -h localhost -d cigionline <name of file>
```

### Elasticsearch
We use Elasticsearch for our search backend, which can be installed with the following command.
``` shell
$ brew tap elastic/tap
$ brew install elastic/tap/elasticsearch-full
```

Elasticsearch can then be started using the command `elasticsearch`. Alternatively, use this to launch Elasticsearch in the background:
``` shell
$ brew services start elastic/tap/elasticsearch-full
```

### Node.js
We use webpack, which is built on Node.js, to bundle our frontend assets. [Instructions to install nvm, a Node.js version manager.](https://github.com/nvm-sh/nvm)

Once you have nvm installed, you can install a version of Node.js with the command `nvm install` followed by the Node.js version number. Here is an example:
``` shell
$ nvm install 14.15.4
```

Finally, install the Node.js packages.
``` shell
$ npm install
```

## Development
To start the Wagtail app, ensure all migrations have been run first.
``` shell
$ python manage.py migrate
```

Then start the Django backend using the following command.
``` shell
$ python manage.py runserver
```

To reindex the search backend, Elasticsearch needs to be running. Once it is, update the search index from Django.
``` shell
$ python manage.py update_index
```

Next, run webpack to watch for changes in the frontend assets.
``` shell
$ npm start
```
