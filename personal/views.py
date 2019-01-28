from personal import app
from flask import render_template

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return "nothing"

@app.route("/projects")
def projects():
    return "nothing"