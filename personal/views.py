from personal import app
from flask import render_template

import requests
from bs4 import BeautifulSoup as bs

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

@app.route("/youtube")
def youtube():
    url = "https://www.youtube.com/feed/trending"

    page = requests.get(url)
    soup = bs(page.content, 'html.parser')

    links = soup.find_all('a', class_="yt-uix-tile-link", href=True)

    html_content = ""

    for x in range(10):

        html_content += str(x+1) + ") " + links[x].text + "<br>"
        html_content += "https://www.youtube.com" + links[x]['href'] + "<br><br>"

    return html_content
