# cigionline

[![Build Status](https://travis-ci.com/CIGIHub/cigionline.svg?branch=master)](https://travis-ci.com/CIGIHub/cigionline)
[![Coverage Status](https://coveralls.io/repos/github/CIGIHub/cigionline/badge.svg)](https://coveralls.io/github/CIGIHub/cigionline)
[![Reviewed by Hound](https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg)](https://houndci.com)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=CIGIHub/cigionline)](https://dependabot.com)

Wagtail source code for cigionline.org


## Development
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
