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


db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor(buffered=True)


@app.route("/api/save-language", methods=["POST"])
def save_language():
    data = request.json
    language = data["language"]
    ip_address = request.remote_addr

    db_cursor.execute(
        "INSERT INTO visitor_languages (ip_address, language) VALUES (%s, %s)",
        (ip_address, language),
    )
    db_connection.commit()

    return jsonify({"message": "Language and IP address saved successfully!"})


# TODO: ADD FINGERPRINT
@app.route("/track-visit", methods=["POST"])
def track_visit():
    try:
        db_connection = mysql.connector.connect(**db_config)
        db_cursor = db_connection.cursor(buffered=True)
        db_cursor.execute("SELECT 1")  # Simple query to test connection
        db_connection.close()
        return jsonify({"message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# def track_visit():
#     db_connection = mysql.connector.connect(**db_config)
#     db_cursor = db_connection.cursor(buffered=True)
#     data = request.get_json(silent=True)
#     if data is None:
#         return jsonify({"error": "No JSON data provided"}), 400

#     ip_address = request.remote_addr
#     current_time = datetime.now()

#     # Check for existing session or user
#     try:
#         db_cursor.execute(
#             "SELECT UserID FROM Users WHERE IPAddress = %s LIMIT 1", (ip_address,)
#         )
#         user_record = db_cursor.fetchone()

#         if user_record:
#             user_id = user_record[0]
#             # Check if there's an ongoing session for this user
#             db_cursor.execute(
#                 """
#                 SELECT SessionID, StartTimestamp FROM Sessions
#                 WHERE UserID = %s AND EndTimestamp IS NULL
#                 ORDER BY StartTimestamp DESC LIMIT 1
#             """,
#                 (user_id,),
#             )
#             session_record = db_cursor.fetchone()

#             if session_record:
#                 # End the current session
#                 session_id, start_timestamp = session_record
#                 db_cursor.execute(
#                     """
#                     UPDATE Sessions SET EndTimestamp = %s
#                     WHERE SessionID = %s
#                 """,
#                     (current_time, session_id),
#                 )
#             else:
#                 # Start a new session if no ongoing session exists
#                 db_cursor.execute(
#                     """
#                     INSERT INTO Sessions (UserID, StartTimestamp)
#                     VALUES (%s, %s)
#                 """,
#                     (user_id, current_time),
#                 )

#         else:
#             # Create new user and start a new session if user does not exist
#             db_cursor.execute(
#                 """
#                 INSERT INTO Users (IPAddress, CreatedAt)
#                 VALUES (%s, %s)
#             """,
#                 (ip_address, current_time),
#             )
#             user_id = db_cursor.lastrowid
#             db_cursor.execute(
#                 """
#                 INSERT INTO Sessions (UserID, StartTimestamp)
#                 VALUES (%s, %s)
#             """,
#                 (user_id, current_time),
#             )

#         db_connection.commit()

#     except Exception as e:
#         db_connection.rollback()
#         return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
