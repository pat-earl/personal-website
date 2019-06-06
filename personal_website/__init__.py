from flask import Flask 
import pymongo
import configparser
import sys

app = Flask(__name__, instance_relative_config=True) 

# Config parser
config = configparser.ConfigParser()

try:
    with open("config.ini") as config_file:
        config.read_file(config_file)
except FileNotFoundError:
    print("config.ini not found\n",
          "Please copy the example_config.ini and enter your details")
    sys.exit(0)

# MonogoDB Client
mongo_config = config['MongoDB']
DB_STRING = "mongodb://{}:{}@{}/{}".format(mongo_config['USER'],
                                           mongo_config['PWD'],
                                           mongo_config['HOST'],
                                           mongo_config['DB'])

try:
    client = pymongo.MongoClient(DB_STRING)
except pymongo.errors.ConnectionFailure as e:
    print("Failed to connect to MongoDB server!")
    sys.exit(0)

db = client.get_default_database()


import personal_website.views

app.config.from_object('config.DevelopmentConfig')