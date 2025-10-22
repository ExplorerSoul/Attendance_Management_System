import mysql.connector
from mysql.connector.errors import InterfaceError
import redis
import time
import json
import ssl
from datetime import datetime  # Import datetime class for parsing
from config import VALKEY_CONFIG, MYSQL_CONFIG, VALKEY_STREAM_NAME, VALKEY_GROUP_NAME, VALKEY_CONSUMER_NAME


# --- Connection Helper Functions ---

def get_mysql_connection(max_retries=5):
    """Establishes a connection to the Aiven MySQL database with retries."""
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            print(" [DB] MySQL connection established.")
            return conn
        except InterfaceError as err:
            print(f" [DB] Error connecting to MySQL (Attempt {attempt + 1}/{max_retries}): {err}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None


def get_valkey_client():
    """Establishes a connection to the Valkey stream."""
    try:
        r = redis.Redis(
            host=VALKEY_CONFIG['host'],
            port=VALKEY_CONFIG['port'],
            password=VALKEY_CONFIG['password'],
            ssl=True,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            ssl_ca_certs=VALKEY_CONFIG['ssl_ca_certs'],
            decode_responses=False
        )
        r.ping()
        print(" [VALKEY] Valkey client connected.")
        return r
    except Exception as e:
        print(f" [VALKEY] Error connecting to Valkey: {e}")
        return None


# --- Main Consumer Logic ---

def process_messages(r, mysql_conn):
    """Reads messages, writes batch to DB, and ACKs them."""

    # 1. Read messages from the stream
    messages = r.xreadgroup(
        groupname=VALKEY_GROUP_NAME,
        consumername=VALKEY_CONSUMER_NAME,
        streams={VALKEY_STREAM_NAME: '>'},
        count=10,  # Batch processing size
        block=10000
    )

    if not messages:
        return

    stream_data = messages[0][1]

    # Prepare data structures
    records_to_insert = []
    message_ids_to_ack = []

    # 1.1 Collect all roll numbers for batch name lookup
    roll_numbers = []
    for msg_id, data in stream_data:
        try:
            payload = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
            roll_numbers.append(payload['roll_no'])
            message_ids_to_ack.append(msg_id)
        except Exception as e:
            print(f" [!!!] Failed to parse message ID {msg_id}: {e}. Skipping and NOT ACKNOWLEDGING.")

    if not roll_numbers:
        return

    # 2. Batch Lookup Student Names
    name_lookup = {}
    try:
        cursor = mysql_conn.cursor()
        # Create a placeholder string for the query: (%s, %s, ...)
        placeholders = ', '.join(['%s'] * len(roll_numbers))

        # Get names for all rolls in the current batch
        lookup_query = f"SELECT roll_no, name FROM students WHERE roll_no IN ({placeholders})"
        cursor.execute(lookup_query, roll_numbers)

        for roll_no, name in cursor.fetchall():
            name_lookup[roll_no] = name
        cursor.close()
    except mysql.connector.Error as e:
        print(f" [!!!] MySQL Name Lookup FAILED: {e}. Cannot process batch.")
        # Rollback is not strictly necessary here, but we exit the function without ACK
        return

    # 3. Prepare Batch Data for Insertion (Iterate over the stream data again)
    for msg_id, data in stream_data:
        try:
            payload = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
            roll_no = payload['roll_no']

            # --- FIX: Parse and format timestamp for MySQL DATE/TIME types ---
            full_timestamp = payload['timestamp']

            # Parse the ISO 8601 string into a datetime object
            dt_object = datetime.fromisoformat(full_timestamp)

            # Format to MySQL DATE ('YYYY-MM-DD') and TIME ('HH:MM:SS')
            attendance_date = dt_object.strftime('%Y-%m-%d')
            attendance_time = dt_object.strftime('%H:%M:%S')

            student_name = name_lookup.get(roll_no, "Unknown Student")

            # Prepare data tuple for MySQL executemany
            records_to_insert.append((
                roll_no,
                student_name,  # Insert name from lookup
                payload['class_id'],
                attendance_time,
                attendance_date
            ))
            # message_ids_to_ack is already populated

        except Exception as e:
            print(f" [!!!] Failed to process message ID {msg_id} during parsing: {e}. Skipping.")
            # We don't remove the message ID from message_ids_to_ack yet, we handle failure in the next step

    # 4. Write Batch to MySQL
    if records_to_insert:
        try:
            cursor = mysql_conn.cursor()
            # Ensure your table structure matches this INSERT statement
            insert_query = """
            INSERT INTO attendance
            (roll_no, name, class_id, time, date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name)
            """
            cursor.executemany(insert_query, records_to_insert)
            mysql_conn.commit()
            cursor.close()

            # 5. Acknowledge messages only after successful DB commit
            r.xack(VALKEY_STREAM_NAME, VALKEY_GROUP_NAME, *message_ids_to_ack)
            print(f" [SUCCESS] Committed {len(records_to_insert)} records and acknowledged messages.")

        except mysql.connector.Error as e:
            print(f" [!!!] MySQL Batch Insert FAILED: {e}. Data remains in stream for retry.")
            # If commit fails, the messages are NOT ACKed, and Valkey will redeliver them later.
            mysql_conn.rollback()  # Ensure transaction is clean
        except Exception as e:
            print(f" [!!!] General error during batch write: {e}")


def start_consumer():
    """Main consumer loop that manages connections."""
    r = None
    mysql_conn = None

    while True:
        # 1. Connect/Reconnect Valkey
        if r is None:
            r = get_valkey_client()
            if r:
                # Initialize the Consumer Group (id='0' means start reading from beginning)
                try:
                    r.xgroup_create(name=VALKEY_STREAM_NAME, groupname=VALKEY_GROUP_NAME, id='0', mkstream=True)
                    print(f" [VALKEY] Consumer group '{VALKEY_GROUP_NAME}' created.")
                except redis.exceptions.ResponseError as e:
                    if 'BUSYGROUP' in str(e):
                        print(f" [VALKEY] Consumer group '{VALKEY_GROUP_NAME}' already exists.")
                    else:
                        print(f" [VALKEY] Error creating group: {e}")

        # 2. Connect/Reconnect MySQL
        if mysql_conn is None or not mysql_conn.is_connected():
            mysql_conn = get_mysql_connection()

        # 3. Process messages only if both services are connected
        if r and mysql_conn:
            process_messages(r, mysql_conn)
        else:
            time.sleep(5)
            print(" [WARNING] Waiting for connections...")


if __name__ == '__main__':
    print(f" [*] Starting Attendance Consumer Worker...")
    start_consumer()
