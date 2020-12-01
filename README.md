# cigionline

[![Django CI](https://github.com/CIGIHub/cigionline/workflows/Django%20CI/badge.svg)](https://github.com/CIGIHub/cigionline/actions?query=workflow%3A%22Django+CI%22)
[![Coverage Status](https://coveralls.io/repos/github/CIGIHub/cigionline/badge.svg)](https://coveralls.io/github/CIGIHub/cigionline)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=CIGIHub/cigionline)](https://dependabot.com)

Wagtail source code for cigionline.org


## Installation
This project uses Python 3.8.5.
``` shell
$ git clone git@github.com:CIGIHub/cigionline.git
$ cd cigionline
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

We use PostgreSQL for our database. Once you have PostgreSQL [installed](https://postgresapp.com), run the following commands to set up your local database.
``` shell
$ create user cigi password 'cigi' superuser
$ create database cigionline
```

If you have a copy of the database file, it can be imported with the following command:
``` shell
$ pg_restore --verbose --clean --no-acl --no-owner -h localhost -d cigionline <name of file>
```

Finally, install the packages for the frontend.
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

Next, run webpack to watch for changes in the frontend assets.
``` shell
$ npm start
```
