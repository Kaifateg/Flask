from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "flask.db")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), nullable=False)
    text = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Заметка {self.title}>"


@app.route("/")
def subjects():
    return render_template("subjects.html")

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
