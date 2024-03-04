from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import mysql.connector
import json
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

load_dotenv(".env")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE_NAME = os.getenv("MYSQL_DATABASE_NAME")

app = Flask(__name__)
CORS(app)
# app.config["CORS_HEADERS"] = "Content-Type"
# CORS(
#     app,
#     resources={
#         r"/api/*": {
#             "origins": [
#                 "https://api.solsonthesquare.online",
#                 "https://www.solsonthesquare.online",
#                 "https://solsonthesquare.online",
#             ]
#         }
#     },
#     supports_credentials=False,
# )

from urllib.parse import quote_plus

# encoded_password = quote_plus(MYSQL_PASSWORD)
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}/{MYSQL_DATABASE_NAME}"
# )
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# from flask_migrate import Migrate

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from mysql.connector import pooling

db_config = {
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "host": MYSQL_HOST,
    "database": MYSQL_DATABASE_NAME,
    "autocommit": True,
    "pool_name": "mysql_pool",
    "pool_size": 5,  # Adjust the pool size to your needs
}

# Create a connection pool
db_pool = pooling.MySQLConnectionPool(**db_config)


# class PageSessions(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     IPAddress = db.Column(db.String(255), nullable=False)
#     sessionStart = db.Column(db.DateTime, nullable=False)
#     sessionEnd = db.Column(db.DateTime)


# class LanguageSelections(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     IPAddress = db.Column(db.String(255), nullable=False)
#     SelectedLanguage = db.Column(db.String(50), nullable=False)
#     CreatedAt = db.Column(db.DateTime, nullable=False)


# class CartItems(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     IPAddress = db.Column(db.String(255), nullable=False)
#     itemName = db.Column(db.String(255), nullable=False)
#     quantity = db.Column(db.Integer, default=1)
#     createdAt = db.Column(db.DateTime, nullable=False)


# class PromotionClicks(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     event = db.Column(db.String(255), nullable=False)
#     timestamp = db.Column(db.DateTime, nullable=False)
#     IPAddress = db.Column(db.String(255), nullable=False)


# class VenmoClicks(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, nullable=False)
#     IPAddress = db.Column(db.String(255), nullable=False)


@app.route("/")
def index():
    return "Hello World from Flask Backend!"


@app.route("/check-db-connection")
def check_db_connection():
    try:
        db_connection = db_pool.get_connection()
        if db_connection.is_connected():
            return jsonify({"message": "Database connection successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if db_connection.is_connected():
            db_connection.close()


@app.route("/track-visit", methods=["POST"])
def track_visit():
    ip_address = request.remote_addr  # Get the IP address of the visitor
    session_start = datetime.now()  # Session start time

    try:
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO PageSessions (IPAddress, sessionStart) VALUES (%s, %s)",
            (ip_address, session_start),
        )
        session_id = db_cursor.lastrowid  # Retrieve the last insert id
        db_connection.commit()

        return (
            jsonify(
                {"message": "Visit tracked successfully.", "sessionId": session_id}
            ),
            200,
        )

    except Exception as e:
        db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
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
        # Get connection from pool
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()
        # db_connection = mysql.connector.connect(**db_config)
        # db_cursor = db_connection.cursor(buffered=True)

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


@app.route("/api/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.json
    itemName = data.get("itemName")  # Ensure this matches your front-end request
    quantity = data.get("quantity", 1)  # Default to 1 if not specified
    current_time = datetime.now()
    ip_address = request.remote_addr  # The IP address of the client making the request

    try:
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO CartItems (IPAddress, itemName, quantity, createdAt) VALUES (%s, %s, %s, %s)",
            (ip_address, itemName, quantity, current_time),
        )
        db_connection.commit()

        return jsonify({"message": "Item added to cart successfully!"}), 200

    except Exception as e:
        if db_connection:
            db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection and db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.route("/update-session-end", methods=["POST"])
def update_session_end():
    data = request.json
    session_id = data.get("sessionId")
    session_end = datetime.now()  # Capture the current time as session end

    try:
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "UPDATE PageSessions SET sessionEnd = %s WHERE id = %s",
            (session_end, session_id),
        )
        db_connection.commit()

        return jsonify({"message": "Session end updated successfully."}), 200

    except Exception as e:
        if db_connection:
            db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection and db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.route("/api/track-promotion-click", methods=["POST"])
def track_promotion_click():
    data = request.json
    event = data.get("event")
    # Convert ISO 8601 format to MySQL DATETIME format
    timestamp = datetime.strptime(data.get("timestamp"), "%Y-%m-%dT%H:%M:%S.%fZ")
    ip_address = request.remote_addr

    try:
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO PromotionClicks (event, timestamp, IPAddress) VALUES (%s, %s, %s)",
            (event, timestamp, ip_address),
        )
        db_connection.commit()
        return jsonify({"message": "Promotion click tracked successfully."}), 200
    except Exception as e:
        if db_connection:
            db_connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if db_connection and db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.route("/api/track-venmo-click", methods=["POST"])
def track_venmo_click():
    ip_address = request.remote_addr  # Get the IP address of the requester
    timestamp = datetime.now()  # Get the current timestamp

    try:
        db_connection = db_pool.get_connection()
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO VenmoClicks (timestamp, IPAddress) VALUES (%s, %s)",
            (timestamp, ip_address),
        )
        db_connection.commit()

        return jsonify({"message": "Venmo click tracked successfully."}), 200

    except Exception as e:
        if db_connection:
            db_connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if db_connection and db_connection.is_connected():
            db_cursor.close()
            db_connection.close()


@app.after_request
def after_request_func(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


if __name__ == "__main__":
    app.run(debug=True)
