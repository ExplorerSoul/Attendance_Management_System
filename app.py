import eventlet  # MUST be imported first for monkey-patching

eventlet.monkey_patch()

import os
import io
import csv
import json
import redis
import ssl
import time
from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
from datetime import datetime, date, time, timedelta
import logging
from config import MYSQL_CONFIG, VALKEY_CONFIG, VALKEY_STREAM_NAME

# Set up logging early
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret')

# Initialize SocketIO, using eventlet as the asynchronous mode
socketio = SocketIO(app, async_mode='eventlet')

# Global state for the background thread and its lock
thread = None
thread_lock = eventlet.semaphore.Semaphore()


# --- Connection Helper Functions ---

def get_connection():
    """Return a new MySQL connection using config. Caller must close."""
    return mysql.connector.connect(**MYSQL_CONFIG)


def get_valkey_client_worker():
    """Establishes a connection to Valkey for the background thread."""
    try:
        r = redis.Redis(
            host=VALKEY_CONFIG['host'],
            port=VALKEY_CONFIG['port'],
            password=VALKEY_CONFIG['password'],
            ssl=True,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            ssl_ca_certs=VALKEY_CONFIG['ssl_ca_certs'],
            # IMPORTANT: Set decode_responses=False for XREAD as stream fields are bytes
            decode_responses=False
        )
        r.ping()
        logging.info(" [VALKEY] Worker client connected.")
        return r
    except Exception as e:
        logging.error(f" [VALKEY] Worker error connecting to Valkey: {e}")
        return None


# --- Background Task: Valkey Stream Reader ---

def valkey_stream_reader():
    """Continuously reads the Valkey stream for new attendance events and broadcasts them."""
    r = get_valkey_client_worker()

    DASHBOARD_GROUP = 'dashboard_readers'

    if r:
        try:
            # We don't use XGROUP READ, but we create a non-durable group just for sanity checks if needed
            r.xgroup_create(name=VALKEY_STREAM_NAME, groupname=DASHBOARD_GROUP, id='0', mkstream=True)
            logging.info(f" [VALKEY] Dashboard reader group '{DASHBOARD_GROUP}' created (non-durable listener).")
        except redis.exceptions.ResponseError as e:
            if 'BUSYGROUP' in str(e):
                logging.info(f" [VALKEY] Dashboard reader group '{DASHBOARD_GROUP}' already exists.")
            else:
                logging.error(f" [VALKEY] Error creating group: {e}")

    # Set initial ID to '0-0' (start of stream) if thread is first running,
    # but we will use the stream's current end ID after the first run.
    # To catch all messages reliably after startup, let's start at the beginning of stream ('0').
    last_id = '0'

    # Attempt to find the actual latest ID if the stream exists
    try:
        if r:
            stream_info = r.xinfo_stream(VALKEY_STREAM_NAME)
            # Use the last ID if the stream has entries, otherwise use '$' for new entries
            if stream_info.get(b'last-generated-id'):
                # Set last_id to the last entry seen plus one, to catch only NEW ones.
                # The '0' initial read below will fetch all, but we ensure it works on subsequent loops.
                last_id = stream_info[b'last-generated-id'].decode()
                logging.info(f" [VALKEY] Starting read from existing stream ID: {last_id}")
            else:
                # If stream is empty, start reading from the next one created
                last_id = '$'
                logging.info(" [VALKEY] Starting read from end of empty stream.")
    except Exception as e:
        logging.warning(f" [VALKEY] Could not determine last stream ID: {e}. Defaulting to '$'.")
        last_id = '$'

    while True:
        if r is None:
            r = get_valkey_client_worker()
            if r is None:
                socketio.sleep(5)
                continue

        try:
            # XREAD is used here. If last_id is '$', it waits for a new message.
            # If last_id is a specific ID, it reads from the next entry.
            messages = r.xread(
                streams={VALKEY_STREAM_NAME: last_id},
                count=10,
                block=5000  # Block for up to 5 seconds
            )

            if messages:
                # messages structure: [[stream_name, [[id, data], [id, data], ...]]]
                stream_data = messages[0][1]

                for msg_id, data in stream_data:
                    # Decode byte keys/values to string before sending over WebSocket
                    payload = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}

                    # Broadcast the new attendance event to all connected clients
                    socketio.emit('new_attendance_event', {
                        'roll_no': payload.get('roll_no'),
                        'class_id': payload.get('class_id')
                    }, namespace='/')

                    last_id = msg_id.decode()  # Update last read ID
                    logging.info(f" [SOCKETIO] Emitted new event for Roll No: {payload.get('roll_no')}")

        except Exception as e:
            logging.error(f" [!!!] Error reading stream/emitting: {e}")
            r = None  # Force reconnect

        socketio.sleep(0.1)  # Yield control to the eventlet loop


# --- SocketIO Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """Fired when a client connects via SocketIO."""
    global thread
    logging.info('Client connected to SocketIO.')

    # Start the background task once, when the first client connects
    with thread_lock:
        if thread is None:
            logging.info('Starting Valkey Stream Reader thread...')
            thread = socketio.start_background_task(valkey_stream_reader)

        # --- Existing Dashboard Functions (omitted for brevity) ---


# ... (rest of app.py is unchanged) ...


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
        # We need to duplicate params because they are used twice in the subqueries
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
        student_attendance=fetch_student_attendance(selected_class_id=selected_class_id, date_from=date_from,
                                                    date_to=date_to),
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
            q += " AND date >= %s";
            params.append(date_from)
        if date_to:
            q += " AND date <= %s";
            params.append(date_to)
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


# --- Main Run Block ---
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true")

    print("\n" + "=" * 60)
    print(f"DASHBOARD URL: http://{host}:{port}/")
    print("========================================================")
    print("NOTE: Ensure producer_service..py and consumer_worker.py are also running.")
    print("========================================================")

    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host=host, port=port, debug=debug_mode)
