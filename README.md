# AWS EC2 Flask + SQLite Web Application

Course project: user registration, login, persistent profile, and text-file upload with word count and download.

## Live demo

http://18.225.218.211/ (EC2 public IP may change if the instance is stopped and restarted).

## Features

- Register a user with username, password, first and last name, email, and address.
- Passwords stored as Werkzeug hashes in SQLite.
- Log out, log in again, and retrieve saved profile details.
- Upload UTF-8 `.txt` files (up to 5 MiB).
- Display a whitespace-delimited word count and download previously uploaded files.
- Restrict profile and downloads to the logged-in user.

## Stack

AWS EC2 (Ubuntu 24.04 LTS), Apache2, mod_wsgi, Python 3, Flask, SQLite3.

## Project structure

```text
flaskapp.py
flaskapp.wsgi
schema.sql
requirements.txt
templates/
  register.html
  login.html
  profile.html
apache/
  shaikaz-flask.conf.example
```

## Deployment outline

1. Launch an Ubuntu EC2 instance, allow HTTP (port 80) and restrict SSH (port 22).
2. Install `apache2`, `libapache2-mod-wsgi-py3`, `python3-flask`, and `sqlite3`.
3. Put the project at `/home/ubuntu/shaikaz-flask` (or update the paths in WSGI and Apache config).
4. Create an empty database with `sqlite3 shaikaz.db < schema.sql`. **Do not run this step to replace the existing EC2 database.**
5. Set permissions so Apache's `www-data` process can read the application, write to the database and its containing directory, and create the uploads directory. Avoid world-writable permissions.
6. Set a strong private `FLASK_SECRET_KEY` in the Apache/mod_wsgi process environment. Do not publish it.
7. Adapt `apache/shaikaz-flask.conf.example`, enable the site, check with `sudo apache2ctl configtest`, and reload Apache.

## Security / submission notes

The live demonstration currently uses plain HTTP; do not enter real passwords or personal addresses. Configure HTTPS and a private production Flask secret before using it with real accounts. The application source includes a temporary development secret fallback, which is not suitable for public production use.

The SQLite database, uploaded files, EC2 private key, and environment secrets are intentionally excluded from this repository. The professor's original Limerick text file is not reproduced here.
