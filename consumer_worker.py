import mysql.connector
from mysql.connector.errors import InterfaceError
import redis
import time
import json
import ssl
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
    # '>': Read new messages that haven't been delivered to any consumer yet
    # block=10000: Wait up to 10 seconds for new messages before looping
    messages = r.xreadgroup(
        groupname=VALKEY_GROUP_NAME,
        consumername=VALKEY_CONSUMER_NAME,
        streams={VALKEY_STREAM_NAME: '>'},
        count=10,  # Batch processing size
        block=10000
    )

    if not messages:
        # print(" [VALKEY] No new messages.")
        return

    # messages structure: [[stream_name, [[id, data], [id, data], ...]]]
    stream_data = messages[0][1]

    # Prepare batch insertion
    records_to_insert = []
    message_ids_to_ack = []

    for msg_id, data in stream_data:
        try:
            # Decode byte keys/values from Redis to string
            payload = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}

            # Prepare data tuple for MySQL executemany
            records_to_insert.append((
                payload['roll_no'],
                payload['class_id'],
                payload['timestamp'],
                payload['timestamp']
            ))
            message_ids_to_ack.append(msg_id)
        except Exception as e:
            print(f" [!!!] Failed to parse message ID {msg_id}: {e}. Skipping and NOT ACKNOWLEDGING.")

    # 2. Write Batch to MySQL
    if records_to_insert:
        try:
            cursor = mysql_conn.cursor()
            # Ensure your table structure matches this INSERT statement
            insert_query = """
            INSERT INTO attendance_records 
            (roll_no, class_id, attendance_date, attendance_time)
            VALUES (%s, %s, DATE(%s), TIME(%s))
            """
            cursor.executemany(insert_query, records_to_insert)
            mysql_conn.commit()
            cursor.close()

            # 3. Acknowledge messages only after successful DB commit
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
