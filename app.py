from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app)

# db_config = {

# }

conn = mysql.connector.connect(host='localhost', password=)