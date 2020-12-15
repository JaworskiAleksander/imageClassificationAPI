from flask import Flask, jsonify, request
from flask_restful import Api, Resources
from pymongo import MongoClient
import bcrypt
# necessary to get the images from URL's provided by users
import requests
import subprocess
import json
