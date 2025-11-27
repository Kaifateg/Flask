from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "flask.db")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config['SECRET_KEY'] = "пример"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), nullable=False)
    text = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Заметка {self.title}>"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_session_token(self):
        self.session_token = secrets.token_urlsafe(32)
        self.token_expiration = datetime.utcnow() + timedelta(minutes=60)
        db.session.commit()
        return self.session_token

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/")
def subjects():
    return render_template("subjects.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Пользователь успешно зарегистрирован")
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username_input = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username_input).first()

        if user and user.check_password(password):
            user.generate_session_token()
            session["user_id"] = user.id
            flash("Вы успешно вошли в систему!")
            return redirect(url_for("prog_notes"))
        else:
            flash("Неверные данные (email или пароль)")
            return render_template("login.html")


@app.before_request
def check_auth():
    allowed_routes = ['login', 'register', 'subjects', 'static', 'home']
    if request.endpoint not in allowed_routes:
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)

            if user and user.token_expiration > datetime.utcnow():
                user.token_expiration = datetime.utcnow() + timedelta(minutes=60)
                db.session.commit()
                return

        flash("Требуется авторизация для доступа к запрашиваемой странице.")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Вы вышли из системы")
    return redirect(url_for("subjects"))


@app.route("/дневник_программиста", methods=["GET", "POST"])
def prog_notes():
    if request.method == "POST":
        title_note = request.form["title_note"]
        note_text = request.form["note"]
        subtitle_note = request.form.get("subtitle_note", "")
        if title_note and note_text:
            new_note = Notes(title=title_note, text=note_text,
                             subtitle=subtitle_note)
            db.session.add(new_note)
            db.session.commit()
        return redirect(url_for("prog_notes"))

    all_notes = Notes.query.all()
    return render_template("notes.html", notes=all_notes)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        pass
    app.run(debug=True)
