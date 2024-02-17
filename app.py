from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import mysql.connector
import json
from dotenv import load_dotenv
import os
import uuid

load_dotenv(".env")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE_NAME = os.getenv("MYSQL_DATABASE_NAME")

app = Flask(__name__)
CORS(app)
# app.config["CORS_HEADERS"] = "Content-Type"

db_config = {
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "host": MYSQL_HOST,
    "database": MYSQL_DATABASE_NAME,
    "autocommit": True,
}

db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()


@app.route("/")
def index():
    return "Hello World from Flask Backend!"


@app.route("/track-visit", methods=["GET"])
def track_visit():
    visitor_id = request.cookies.get("visitor_ud")
    ip_address = request.remote_addr

    if not visitor_id:
        visitor_id = uuid.uuid4().hex
        response = make_response(jsonify({"message": "New visitor tracked"}))
        response.set_cookie(
            "visitor_id", visitor_id, max_age=60 * 60 * 24 * 365
        )  # Expires in 1 year
    else:
        response = jsonify({"message": "Returning visitor tracked"})

    db_cursor.execute("SELECT CookieID FROM Users WHERE CookieID = %s", (visitor_id,))
    result = db_cursor.fetchone()

    if not result:
        db_cursor.execute(
            "INSERT INTO Users (CookieID, IPAddress) VALUES (%s,%s)",
            (visitor_id, ip_address),
        )
        db_connection.commit()

    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
