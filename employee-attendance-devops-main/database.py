
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://attendance_user:attendance_pass@localhost:5432/attendance_db"
)


def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    for attempt in range(10):
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    department VARCHAR(100) NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER REFERENCES employees(id)
                        ON DELETE CASCADE,
                    attendance_date DATE NOT NULL,
                    status VARCHAR(20) NOT NULL
                        CHECK (status IN ('Present', 'Absent')),
                    UNIQUE(employee_id, attendance_date)
                )
            """)

            conn.commit()
            cur.close()
            conn.close()

            print("PostgreSQL database initialized!")
            return

        except psycopg2.OperationalError:
            if attempt == 9:
                raise
            print("Waiting for PostgreSQL...")
            time.sleep(2)


def get_employees():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employees ORDER BY id DESC")
    employees = cur.fetchall()

    cur.close()
    conn.close()

    return employees


def add_employee(name, email, department):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO employees (name, email, department)
        VALUES (%s, %s, %s)
        RETURNING *
    """, (name, email, department))

    employee = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return employee


def mark_attendance(employee_id, attendance_date, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance
        (employee_id, attendance_date, status)
        VALUES (%s, %s, %s)
        ON CONFLICT (employee_id, attendance_date)
        DO UPDATE SET status = EXCLUDED.status
        RETURNING *
    """, (employee_id, attendance_date, status))

    record = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return record


def get_attendance():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            attendance.id,
            employees.name,
            employees.department,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN employees
        ON attendance.employee_id = employees.id
        ORDER BY attendance.attendance_date DESC,
                 attendance.id DESC
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    return records
