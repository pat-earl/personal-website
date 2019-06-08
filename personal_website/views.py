from personal_website import app, config, client, db
from flask import render_template, jsonify, make_response, abort

import requests
from bs4 import BeautifulSoup as bs

import pymongo
import datetime
import dateutil.parser

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
@app.route("/bandwidth/")
def bandwidth():
    return render_template("bandwidth.html")

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

        Parameters:
            * Source - The MongoDB collection to query data from 
            * Interface - The interface within the collection to gather data from
            * Interval - The number of seconds to group the data into 
            * Start - The start date for the data (Format: MMDDYYYY)
            * End - The end date for the data (Format: MMDDYYYY)
    '''

    # If no date values are passed, do the last 30 days from today by default
    if start is None: 
        end = datetime.datetime.now()
        print("Default start datetime:", end)
        start = end + datetime.timedelta(days=-2) 
        print("Default end datetime:", start)

    # Otherwise it is given, convert it to datetime
    else:
        start = datetime.datetime.strptime(start, "%m%d%Y")
        end = datetime.datetime.strptime(end, "%m%d%Y")
        print(start.isoformat())
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
            "$gte": start.isoformat(),
            "$lt": end.isoformat()
        }
    }).sort([("time", 1)])

    return_dict = {
        "interval": interval,
        "data": {}
    }

    cur_interval_time = None
    cur_interval_time_str = ""

    for doc in cursor:
        doc_time = dateutil.parser.parse(doc['time'])
        
        if cur_interval_time == None:
            cur_interval_time = doc_time
            cur_interval_time_str = cur_interval_time.strftime("%m-%d-%Y %H:%M:%S")
            return_dict["data"][cur_interval_time_str] = {
                "sent": 0,
                "recv": 0
            }

        
        if ((doc_time + datetime.timedelta(seconds=-interval)) 
                > cur_interval_time):
            cur_interval_time = None
        
        return_dict["data"][cur_interval_time_str]['sent'] += doc['send']
        return_dict["data"][cur_interval_time_str]['recv'] += doc['recv']
    
    return jsonify(return_dict)
