from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import json
from dotenv import load_dotenv
import os

load_dotenv('.env')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
app = Flask(__name__)
CORS(app)

db_config = {
    'user': 'root',
    'password': MYSQL_PASSWORD,
    'host': 'localhost',
    'database': 'sols'
}

db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()

@app.route('/')
def index():
    return "Hello World from Flask Backend!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)