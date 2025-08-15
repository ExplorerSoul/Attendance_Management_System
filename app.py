# app.py
import os
import io
import csv
import json
from flask import Flask, render_template, request, send_file, jsonify
import mysql.connector
from datetime import datetime, date, time, timedelta
import logging
from config import MYSQL_CONFIG

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_connection():
    """Return a new MySQL connection using config. Caller must close."""
    return mysql.connector.connect(**MYSQL_CONFIG)


def fetch_classes():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT class_id, class_name FROM classes ORDER BY class_name")
        return cur.fetchall()
    finally:
        conn.close()


def count_total_students():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        return cur.fetchone()[0]
    finally:
        conn.close()


def count_total_records():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM attendance")
        return cur.fetchone()[0]
    finally:
        conn.close()


def fetch_class_overview(date_from=None, date_to=None):
    """Return per-class overview: (class_id, class_name, total_sessions, total_attendances, avg_pct)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        date_clause = ""
        params = []
        if date_from:
            date_clause += " AND a.date >= %s"
            params.append(date_from)
        if date_to:
            date_clause += " AND a.date <= %s"
            params.append(date_to)

        q = f"""
            SELECT c.class_id, c.class_name,
              (SELECT COUNT(DISTINCT a.date) FROM attendance a WHERE a.class_id = c.class_id {date_clause}) AS total_sessions,
              (SELECT COUNT(*) FROM attendance a WHERE a.class_id = c.class_id {date_clause}) AS total_attendances
            FROM classes c
            ORDER BY c.class_name
        """
        cur.execute(q, params * 2)
        rows = cur.fetchall()

        # total students for percent denominator
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM students")
        total_students = cur2.fetchone()[0] or 0

        overview = []
        for class_id, class_name, total_sessions, total_attendances in rows:
            ts = int(total_sessions or 0)
            ta = int(total_attendances or 0)
            avg_pct = round((ta / (total_students * ts) * 100) if (ts > 0 and total_students > 0) else 0.0, 1)
            overview.append((class_id, class_name, ts, ta, avg_pct))
        return overview
    finally:
        conn.close()


def fetch_student_attendance(selected_class_id=None, date_from=None, date_to=None):
    """Return list of dicts: roll_no, name, attended_sessions, total_sessions, percentage."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)

        # total_sessions (denominator)
        if selected_class_id:
            q_sessions = "SELECT COUNT(DISTINCT date) AS total_sessions FROM attendance WHERE class_id = %s"
            params = [selected_class_id]
            if date_from:
                q_sessions += " AND date >= %s"
                params.append(date_from)
            if date_to:
                q_sessions += " AND date <= %s"
                params.append(date_to)
            cur.execute(q_sessions, params)
            total_sessions = cur.fetchone()['total_sessions'] or 0
        else:
            q_sessions = "SELECT COUNT(DISTINCT class_id, date) AS total_sessions FROM attendance WHERE 1=1"
            params = []
            if date_from:
                q_sessions += " AND date >= %s"
                params.append(date_from)
            if date_to:
                q_sessions += " AND date <= %s"
                params.append(date_to)
            cur.execute(q_sessions, params)
            total_sessions = cur.fetchone()['total_sessions'] or 0

        # student attendance
        if selected_class_id:
            q = """
                SELECT s.roll_no, s.name, COUNT(DISTINCT a.date) AS attended_sessions
                FROM students s
                LEFT JOIN attendance a
                  ON s.roll_no = a.roll_no AND a.class_id = %s
            """
            params = [selected_class_id]
        else:
            q = """
                SELECT s.roll_no, s.name, COUNT(DISTINCT a.class_id, a.date) AS attended_sessions
                FROM students s
                LEFT JOIN attendance a
                  ON s.roll_no = a.roll_no
            """
            params = []

        # date filters in JOIN
        date_filters_on = ""
        if date_from:
            date_filters_on += " AND a.date >= %s"
            params.append(date_from)
        if date_to:
            date_filters_on += " AND a.date <= %s"
            params.append(date_to)

        q = q.replace("ON s.roll_no = a.roll_no", "ON s.roll_no = a.roll_no " + date_filters_on)
        q += " GROUP BY s.roll_no, s.name ORDER BY s.roll_no"
        cur.execute(q, params)
        rows = cur.fetchall()

        result = []
        for r in rows:
            attended = int(r['attended_sessions'] or 0)
            total = int(total_sessions or 0)
            pct = round((attended / total * 100) if total > 0 else 0.0, 1)
            result.append({
                'roll_no': r['roll_no'],
                'name': r['name'],
                'attended': attended,
                'total_sessions': total,
                'percentage': pct
            })
        return result
    finally:
        conn.close()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    if isinstance(obj, timedelta):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


@app.route("/", methods=["GET"])
def index():
    classes = fetch_classes()
    return render_template(
        "index.html",
        classes=classes,
        selected_class=None,
        selected_date_from="",
        selected_date_to="",
        total_students=count_total_students(),
        total_classes=len(classes),
        total_records=count_total_records(),
        class_overview=fetch_class_overview(),
        student_attendance=fetch_student_attendance(),
        message=None
    )


@app.route("/view", methods=["POST"])
def view():
    classes = fetch_classes()
    selected_class = request.form.get("class_id")
    date_from = request.form.get("date_from") or None
    date_to = request.form.get("date_to") or None

    # date validation
    for d in (date_from, date_to):
        if d:
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                return render_template(
                    "index.html",
                    classes=classes,
                    selected_class=selected_class,
                    selected_date_from=date_from or "",
                    selected_date_to=date_to or "",
                    total_students=count_total_students(),
                    total_classes=len(classes),
                    total_records=count_total_records(),
                    class_overview=fetch_class_overview(),
                    student_attendance=[],
                    message="Invalid date format. Use YYYY-MM-DD."
                )

    selected_class_id = int(selected_class) if selected_class and selected_class.isdigit() else None

    return render_template(
        "index.html",
        classes=classes,
        selected_class=selected_class_id,
        selected_date_from=date_from or "",
        selected_date_to=date_to or "",
        total_students=count_total_students(),
        total_classes=len(classes),
        total_records=count_total_records(),
        class_overview=fetch_class_overview(date_from=date_from, date_to=date_to),
        student_attendance=fetch_student_attendance(selected_class_id=selected_class_id, date_from=date_from, date_to=date_to),
        message=None
    )


@app.route("/export_csv", methods=["GET"])
def export_csv():
    class_id = request.args.get("class_id")
    date_from = request.args.get("date_from") or None
    date_to = request.args.get("date_to") or None
    selected_class_id = int(class_id) if class_id and class_id.isdigit() else None

    rows = fetch_student_attendance(selected_class_id=selected_class_id, date_from=date_from, date_to=date_to)

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["Roll No", "Name", "Attended", "Sessions", "Percentage"])
    for r in rows:
        cw.writerow([r['roll_no'], r['name'], r['attended'], r['total_sessions'], r['percentage']])
    mem = io.BytesIO()
    mem.write(si.getvalue().encode("utf-8"))
    mem.seek(0)
    filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=filename)


@app.route("/student/<roll_no>/attendance", methods=["GET"])
def student_detail(roll_no):
    date_from = request.args.get("date_from") or None
    date_to = request.args.get("date_to") or None
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        q = """
            SELECT a.date, a.time, c.class_name
            FROM attendance a
            JOIN classes c ON a.class_id = c.class_id
            WHERE a.roll_no = %s
        """
        params = [roll_no]
        if date_from:
            q += " AND a.date >= %s"
            params.append(date_from)
        if date_to:
            q += " AND a.date <= %s"
            params.append(date_to)
        q += " ORDER BY a.date DESC, a.time DESC"
        cur.execute(q, params)
        rows = cur.fetchall()

        # Serialize date/time objects
        return app.response_class(
            response=json.dumps(rows, default=json_serial),
            mimetype='application/json'
        )
    finally:
        conn.close()


@app.route("/class_trend/<int:class_id>", methods=["GET"])
def class_trend(class_id):
    date_from = request.args.get("date_from") or None
    date_to = request.args.get("date_to") or None
    conn = get_connection()
    try:
        cur = conn.cursor()
        q = "SELECT date, COUNT(DISTINCT roll_no) as count FROM attendance WHERE class_id = %s"
        params = [class_id]
        if date_from:
            q += " AND date >= %s"; params.append(date_from)
        if date_to:
            q += " AND date <= %s"; params.append(date_to)
        q += " GROUP BY date ORDER BY date"
        cur.execute(q, params)
        rows = cur.fetchall()
        labels = [r[0] for r in rows]
        data = [int(r[1]) for r in rows]
        return app.response_class(
            response=json.dumps({"labels": labels, "data": data}, default=json_serial),
            mimetype='application/json'
        )
    finally:
        conn.close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true"))
