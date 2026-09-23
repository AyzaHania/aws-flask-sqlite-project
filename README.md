# AWS EC2 Flask + SQLite Web Application

Course project: user registration, login, persistent profile, and text-file upload with word count and download.

## EC2 webpage addresses

- Public IPv4 address: http://18.225.218.211/ — Student Portal was confirmed to open here.
- EC2 public DNS: http://ec2-18-225-218-211.us-east-2.compute.amazonaws.com/ — **verify in a browser before submitting as the working webpage URL**. The server-side Host-header check returned Student Portal, but the external browser was still showing the Ubuntu Apache default page at the last check.

Both addresses may change when the EC2 instance stops/starts unless the public IP is retained. Use the EC2 console's **Public IPv4 DNS** field to confirm the current hostname.

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
static/
  style.css
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
3. Install Python dependencies with `python3 -m pip install -r requirements.txt` in an appropriate virtual environment (or use the distribution-provided Flask package). Put the project at `/home/ubuntu/shaikaz-flask` (or update the paths in WSGI and Apache config).
4. Create an empty database with `sqlite3 shaikaz.db < schema.sql`. **Do not run this step to replace the existing EC2 database.**
5. Set permissions so Apache's `www-data` process can read the application, write to the database and its containing directory, and create the uploads directory. Avoid world-writable permissions.
6. Set a strong private `FLASK_SECRET_KEY` in the Apache/mod_wsgi process environment. Do not publish it.
7. Check `apache/shaikaz-flask.conf.example` against the current public DNS and IP, then enable the Flask site, disable the Ubuntu default site, run `sudo apache2ctl configtest`, and reload Apache. Do not reload if the syntax test fails.

### Apache site configuration used on EC2

The saved example in `apache/shaikaz-flask.conf.example` matches the configuration shown in the EC2 terminal:

- `ServerName ec2-18-225-218-211.us-east-2.compute.amazonaws.com`
- `ServerAlias 18.225.218.211`
- mod_wsgi points to `/home/ubuntu/shaikaz-flask/flaskapp.wsgi`.

The EC2 terminal's `sudo apache2ctl -S` output showed the Flask site as the only `*:80` virtual host. Running

```bash
curl -sSL -H "Host: ec2-18-225-218-211.us-east-2.compute.amazonaws.com" http://127.0.0.1/ | head -n 15
```

returned the `Log in · Student Portal` HTML title. This confirms the **local Apache Host-header test**, not successful external browser access to the DNS URL. An internal lookup returning the instance's private address can occur with AWS EC2 private DNS resolution. No SQLite database, uploads, or application logic was changed during this hostname troubleshooting.

### Updating the page design on the running instance

The current repository templates display **Student Portal** and **Welcome** (the former Bloom branding was removed). To copy the current templates and stylesheet onto the server, back up the existing templates and copy from a fresh repository checkout or update an existing checkout before copying. Do **not** replace `shaikaz.db` or the `uploads/` directory.

## Security / submission notes

The live demonstration currently uses plain HTTP; do not enter real passwords or personal addresses. Configure HTTPS and a private production Flask secret before using it with real accounts. The application source includes a temporary development secret fallback, which is not suitable for public production use.

The SQLite database, uploaded files, EC2 private key, and environment secrets are intentionally excluded from this repository. The professor's original Limerick text file is not reproduced here.
