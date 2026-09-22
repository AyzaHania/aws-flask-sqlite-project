import os
import sqlite3

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# We will configure a private production secret before Apache deployment.
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "temporary-development-secret"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "shaikaz.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_uploads_table():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


initialize_uploads_table()


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        firstname = request.form["firstname"].strip()
        lastname = request.form["lastname"].strip()
        email = request.form["email"].strip()
        address = request.form["address"].strip()

        if not all([
            username, password, firstname,
            lastname, email, address
        ]):
            flash("Please complete all fields.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        try:
            with get_db() as connection:
                connection.execute("""
                    INSERT INTO users
                    (username, password, firstname,
                     lastname, email, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    username, hashed_password, firstname,
                    lastname, email, address
                ))
        except sqlite3.IntegrityError:
            flash("That username is already taken.")
            return redirect(url_for("register"))

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        with get_db() as connection:
            user = connection.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    with get_db() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        uploads = connection.execute("""
            SELECT * FROM uploads
            WHERE user_id = ?
            ORDER BY id DESC
        """, (session["user_id"],)).fetchall()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html", user=user, uploads=uploads
    )


@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename:
        flash("Please select a text file.")
        return redirect(url_for("profile"))

    original_filename = secure_filename(uploaded_file.filename)

    if not original_filename.lower().endswith(".txt"):
        flash("Only .txt files are allowed.")
        return redirect(url_for("profile"))

    content = uploaded_file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        flash("Please upload a UTF-8 text file.")
        return redirect(url_for("profile"))

    word_count = len(text.split())

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    import uuid
    stored_filename = (
        uuid.uuid4().hex + "_" + original_filename
    )

    file_path = os.path.join(
        UPLOAD_FOLDER, stored_filename
    )

    with open(file_path, "wb") as saved_file:
        saved_file.write(content)

    with get_db() as connection:
        connection.execute("""
            INSERT INTO uploads
            (user_id, original_filename,
             stored_filename, word_count)
            VALUES (?, ?, ?, ?)
        """, (
            session["user_id"], original_filename,
            stored_filename, word_count
        ))

    flash(f"File uploaded! Word count: {word_count}")
    return redirect(url_for("profile"))


@app.route("/download/<int:upload_id>")
def download(upload_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    with get_db() as connection:
        uploaded_file = connection.execute("""
            SELECT * FROM uploads
            WHERE id = ? AND user_id = ?
        """, (upload_id, session["user_id"])).fetchone()

    if uploaded_file is None:
        return "File not found.", 404

    return send_from_directory(
        UPLOAD_FOLDER,
        uploaded_file["stored_filename"],
        as_attachment=True,
        download_name=uploaded_file["original_filename"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False)
