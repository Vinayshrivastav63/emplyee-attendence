
from flask import Flask, render_template, request, jsonify
from datetime import date
from database import (
    init_db,
    get_employees,
    add_employee,
    mark_attendance,
    get_attendance
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "OK",
        "application": "Employee Attendance System"
    }), 200


@app.route("/api/employees", methods=["GET"])
def employees():
    try:
        return jsonify(get_employees()), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/employees", methods=["POST"])
def create_employee():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    department = data.get("department", "").strip()

    if not name or not email or not department:
        return jsonify({
            "error": "Name, email and department are required"
        }), 400

    try:
        employee = add_employee(name, email, department)
        return jsonify(employee), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/attendance", methods=["GET"])
def attendance():
    try:
        return jsonify(get_attendance()), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/attendance", methods=["POST"])
def create_attendance():
    data = request.get_json(silent=True) or {}

    employee_id = data.get("employee_id")
    attendance_date = data.get("attendance_date", str(date.today()))
    status = data.get("status")

    if not employee_id or status not in ["Present", "Absent"]:
        return jsonify({
            "error": "Valid employee ID and attendance status are required"
        }), 400

    try:
        record = mark_attendance(
            employee_id,
            attendance_date,
            status
        )
        return jsonify(record), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
