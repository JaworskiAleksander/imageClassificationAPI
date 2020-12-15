from flask import Flask, jsonify, request
from flask_restful import Api, Resources
from pymongo import MongoClient
import bcrypt
# necessary to get the images from URL's provided by users
import requests
import subprocess
import json

# initialize flask_restful application
app = Flask(__name__)
api = Api(app)

# initialize mongo database connection
client = MongoClient('mongodb://db:27017')
database = client['ImageRecognition']
collection = database['Users']


class Register(Resource):
    def post(self):
        # Step 1 - retrieve data sent via request by user
        postedData = request.get_json()

        # Step 2 - decompose data into proper variables
        username = postedData['username']
        password = postedData['password']

        # Step 3 - invalid username
        if userExists(username):
            retJSON = {
                'status':       301,
                'message':      'invalid username'
            }
            return jsonify(retJSON)

        # Step 4 - hash the password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
