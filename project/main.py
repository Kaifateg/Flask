from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

notes = {}

@app.route("/")
def subjects():
    return render_template("subjects.html")

@app.route("/дневник_программиста", methods=["GET", "POST"])
def prog_notes():
    if request.method == "POST":
        title_note = request.form["title_note"]
        note = request.form["note"]
        if title_note and note:
            notes[title_note] = note
        return redirect(url_for("prog_notes"))
    return render_template("notes.html", notes=notes)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
