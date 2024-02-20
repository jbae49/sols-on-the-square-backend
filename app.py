from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import mysql.connector
import json
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime


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


@app.route("/")
def index():
    return "Hello World from Flask Backend!"


@app.route("/track-visit", methods=["POST"])
def track_visit():
    ip_address = request.remote_addr  # Get the IP address of the visitor
    current_time = datetime.now()  # Get the current time

    try:
        # Connect to the database

        db_connection = mysql.connector.connect(**db_config)
        db_cursor = db_connection.cursor(buffered=True)
        # Insert every visit into the Users table
        db_cursor.execute(
            "INSERT INTO Visits (IPAddress, CreatedAt) VALUES (%s, %s)",
            (ip_address, current_time),
        )
        db_connection.commit()  # Ensure the transaction is committed to save the data

        return jsonify({"message": "Visit tracked and saved successfully."}), 200

    except Exception as e:
        # If an error occurs, rollback the transaction and return an error message
        db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection and cursor
        if db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.route("/api/save-language", methods=["POST"])
def save_language():
    data = request.json
    language = data["language"]
    ip_address = request.remote_addr
    current_time = datetime.now()

    try:
        db_connection = mysql.connector.connect(**db_config)
        db_cursor = db_connection.cursor(buffered=True)

        db_cursor.execute(
            "INSERT INTO LanguageSelections (IPAddress, SelectedLanguage, CreatedAt) VALUES (%s, %s, %s)",
            (ip_address, language, current_time),
        )
        db_connection.commit()

        return jsonify({"message": "Language selection saved successfully!"}), 200

    except Exception as e:
        db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.after_request
def after_request_func(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
