from personal_website import app, config, client, db
from flask import render_template, jsonify, make_response, abort

import requests
from bs4 import BeautifulSoup as bs

import pymongo
import datetime

# Personal Website stuff
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


# Grabs and displays the current top 10 items on youtube's trending page
# This is here to prove how easy to do a similar thing from PHP was in Python
@app.route("/youtube")
def youtube():
    url = "https://www.youtube.com/feed/trending"

    page = requests.get(url)
    soup = bs(page.content, 'html.parser')

    links = soup.find_all('a', class_="yt-uix-tile-link", href=True)

    html_content = ""

    for x in range(10):

        html_content += str(x+1) + ")"
        html_content += "<a href='https://www.youtube.com" + links[x]['href'] + "'>"
        html_content += links[x].text + "</a><br><br>"

    return html_content


# Bandwidth Monitor Project
@app.route("/bandwidth")
def bandwidth():
    try: 
        client = pymongo.MongoClient(MONGO_DB_STRING)
    except pymongo.errors.ConnectionFailure as e:
        err_str = "PyMongo Error on Connection!<br>"
        err_str += "Message: " + e.message()
        return err_str

# API Calls for it

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found", 
                                  "message": error.description}), 
                                  404)

@app.route("/bandwidth/api/v1/sources", methods=['GET'])
def get_sources():
    '''
        Path: ./api/v1/sources
        Description:
            Returns the available sources to pull data from.
            The sources are the different collections in the MongoDB
    '''
    sources = [collection for collection in client[config['MongoDB']['DB']].collection_names()]
    sources = {"sources" : sources}
    return jsonify(sources)

@app.route("/bandwidth/api/v1/<source>/interfaces", methods=['GET'])
def get_interfaces(source):
    '''
        Path: ./api/v1/<source>/interfaces
        Description:
            Returns the available interfaces 
    '''
    interfaces = db[source].distinct('interface')
    if interfaces == []:
        return abort(404)
    interfaces = {"interfaces": interfaces}
    return jsonify(interfaces)

@app.route("/bandwidth/api/v1/<source>/<interface>/<int:interval>/", 
            methods=['GET'],
            defaults={"start": None, "end": None})
@app.route("/bandwidth/api/v1/<source>/<interface>/<int:interval>/<start>/<end>/",
            methods=['GET'])
def get_bandwidth(source, interface, interval, start, end):
    '''
        Path: ./api/v1/<source>/<interface>/<interval>/<start>/<end>/
        Description:
            Displays the number of megabytes sent in the given interval (seconds)
    '''

    # If no date values are passed, do the last 30 days from today by default
    if start is None: 
        start = datetime.datetime.now()
        print(start)
        end = start + datetime.timedelta(days=-30) 
        print(end)

    # Make sure valid arguments are passed
    try:
        if source not in db.collection_names():
            raise IndexError("Invalid Source")
        interfaces = db[source].distinct('interface')
        if interfaces == []:
            raise IndexError("Invalid source")
        if interface not in interfaces:
            raise IndexError("Invalid interface")

    except IndexError as e:
        abort(404, str(e))

    # Generate the cursor to grab all the documents that are in the given range
    cursor = db[source].find({
        "interface": interface,
        "time": {
            "$gte": end.isoformat(),
            "$lt": start.isoformat()
        }
    })

    return_dict = {
        "interval": interval
    }

    cur_interval = interval

    for doc in cursor:
        time = datetime.datetime.strptime(doc['time'], "%Y-%m-%dT%H:%M:%S%z")
        cur_interval -= time.total_second

        break
    
    return jsonify([test])
