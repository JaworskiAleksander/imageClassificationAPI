from flask import Flask, jsonify, request
from flask_restful import Api, Resource
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
users = database['Users']


def userExists(username):
    return bool(
        users.count_documents({
            'Username': username
        })
    )


def generateReturnDictionary(status, message):
    retJSON = {
        'status':   status,
        'message':  message
    }
    return retJSON


def verifyPassword(username, password):
    if not userExists(username):
        return generateReturnDictionary(301, 'invalid username'), True

    hashed_password = users.find({
        'Username':     username
    })[0]['Password']

    return bcrypt.hashpw(password.encode('utf-8'), hashed_password) == hashed_password


def verifyCredentials(username, password):
    if not userExists(username):
        return generateReturnDictionary(301, 'invalid username'), True

    correct_password = verifyPassword(username, password)
    if not correct_password:
        return generateReturnDictionary(302, 'invalid password'), True

    return None, False


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

        # Step 5 - store user data into database
        users.insert_one({
            'Username':     username,
            'Password':     hashed_password,
            'Tokens':       4
        })

        # Step 6 - return status 200
        retJSON = {
            'status':       200,
            'message':      f'User {username} stored in database successfully!'
        }

        return jsonify(retJSON)


class Classify(Resource):
    def post(self):
        # step 1 - retrieve data sent via request by user
        postedData = request.get_json()

        # Step 2 - decompose postedData into variables
        username = postedData['username']
        password = postedData['password']
        url = postedData['url']

        # Step 3 - verify user credentials
        retJSON, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJSON)

        # Step 4 - check tokens available
        tokens = users.find({
            'Username': username
        })[0]['Tokens']

        if tokens <= 0:
            return jsonify(generateReturnDictionary(303, 'Not Enough Tokens'))

        # Step 5 - download an image provided by user in url
        r = requests.get(url)
        retJSON = {}
        with open('temp.jpg', 'wb') as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg',
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            ret = proc.communicate()[0]
            proc.wait()
            with open('text.txt') as g:
                retJSON = json.load(g)

        # Step 6 - remove 1 token from user
        users.update_one(
            {
                'Username':     username
            },
            {
                "$set": {
                    'Tokens':   tokens - 1
                }
            }
        )

        # Step 7 - return response
        return retJSON


class Refill(Resource):
    def post(self):
        # Step 1 - retrieve data sent by user via request
        postedData = request.get_json()

        # Step 2 - decompose data from postedData
        username = postedData['username']
        password = postedData['admin_password']
        amount = postedData['token_count']

        # Step 3 - validate user
        if not userExists(userExists):
            return jsonify(generateReturnDictionary(301, 'invalid username'))

        # this is NOT how you should do this!
        correct_password = 'abc123'
        if password != correct_password:
            return jsonify(generateReturnDictionary(304, 'invalid admin password'))

        # Step 4 - update users token count
        users.update_one(
            {
                'Username':     username
            },
            {
                '$inc': {
                    'Tokens':   amount
                }
            }
        )

        # Step 5 - return success message
        return jsonify(generateReturnDictionary(200, 'Refilled successfully'))


api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/refill')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
