from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import json
from dotenv import load_dotenv
import os
import uuid

load_dotenv(".env")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
app = Flask(__name__)
CORS(app)

db_config = {
    "user": "root",
    "password": MYSQL_PASSWORD,
    "host": "localhost",
    "database": "sols",
}

db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()


@app.route("/")
def index():
    return "Hello World from Flask Backend!"


@app.route("/track-visit", methods=["GET"])
def track_visit():
    visitor_id = request.cookies.get("visitor_ud")

    db_cursor.execute("SELECT CookieID FROM Users WHERE CookieID = %s", (user_ip,))
    result = db_cursor.fetchone()

    if not result:
        db_cursor.execute("INSERT INTO Users (CookieID) VALUES (%s)", (user_ip,))
        db_connection.commit()

    return jsonify({"message": "Visit recorded"}), 200


# @app.route('/select-language', methods=['POST'])
# def select_language():
#     data = request.get_json()
#     language = data.get('language')

#     user_ip = request.remote_addr
#     print('User IP:', user_ip)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
