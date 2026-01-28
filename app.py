from flask import Flask, render_template, request, jsonify, Response
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import pandas as pd

from utils.face_utils import FaceRecognitionSystem
from utils.anti_spoof import AntiSpoofDetector

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["UPLOAD_FOLDER"] = "data/faces"
app.config["ATTENDANCE_FOLDER"] = "data/attendance"

# Initialize systems
face_system = FaceRecognitionSystem()
anti_spoof = AntiSpoofDetector()

# Global camera
camera = None


# -------------------- ROUTES --------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html")


@app.route("/records")
def records_page():
    records = face_system.get_attendance_records()
    return render_template("records.html", records=records)


# -------------------- API --------------------

@app.route("/api/register", methods=["POST"])
def register_face():
    try:
        data = request.json
        name = data.get("name")
        user_id = data.get("user_id")
        image_data = data.get("image")

        if not all([name, user_id, image_data]):
            return jsonify({"success": False, "message": "Missing required fields"})

        image = face_system.decode_image(image_data)

        if not anti_spoof.is_real_face(image):
            return jsonify({"success": False, "message": "Spoof detected! Please use a real face."})

        success, message = face_system.register_face(name, user_id, image)
        return jsonify({"success": success, "message": message})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/mark_attendance", methods=["POST"])
def mark_attendance():
    try:
        data = request.json
        image_data = data.get("image")
        action = data.get("action")  # punch-in / punch-out

        if not all([image_data, action]):
            return jsonify({"success": False, "message": "Missing required fields"})

        image = face_system.decode_image(image_data)

        if not anti_spoof.is_real_face(image):
            return jsonify({"success": False, "message": "Spoof detected! Please use a real face."})

        name, user_id, confidence = face_system.identify_face(image)

        if name == "Unknown":
            return jsonify({"success": False, "message": "Face not recognized. Please register first."})

        success, message = face_system.mark_attendance(user_id, name, action)

        return jsonify({
            "success": success,
            "message": message,
            "name": name,
            "user_id": user_id,
            "confidence": confidence,
            "action": action
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/identify", methods=["POST"])
def identify():
    try:
        data = request.json
        image_data = data.get("image")

        if not image_data:
            return jsonify({"success": False, "message": "No image provided"})

        image = face_system.decode_image(image_data)
        name, user_id, confidence = face_system.identify_face(image)

        return jsonify({
            "success": True,
            "name": name,
            "user_id": user_id,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/get_registered_users")
def get_registered_users():
    users = face_system.get_registered_users()
    return jsonify({"success": True, "users": users})


@app.route("/api/attendance_report")
def attendance_report():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    report = face_system.get_attendance_report(start_date, end_date)
    return jsonify({"success": True, "report": report})


# -------------------- VIDEO STREAM --------------------

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def generate_frames():
    global camera
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        face_locations = face_recognition.face_locations(frame)

        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


# -------------------- MAIN --------------------

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ATTENDANCE_FOLDER"], exist_ok=True)
    os.makedirs("models", exist_ok=True)

    app.run(host="0.0.0.0", port=5000)
