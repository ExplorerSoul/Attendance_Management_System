from flask import Flask, request, jsonify
from datetime import datetime
import redis
import json
import ssl
import time
from config import VALKEY_CONFIG, VALKEY_STREAM_NAME

app = Flask(__name__)

# --- Valkey Client Initialization ---
def get_valkey_client():
    """Returns a connected Redis/Valkey client, or None on failure."""
    try:
        # Aiven Valkey/Redis usually uses 'redis-py' with SSL
        r = redis.Redis(
            host=VALKEY_CONFIG['host'],
            port=VALKEY_CONFIG['port'],
            password=VALKEY_CONFIG['password'],
            ssl=True,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            ssl_ca_certs=VALKEY_CONFIG['ssl_ca_certs'],
            decode_responses=False # Keep stream data as bytes for efficiency
        )
        r.ping()
        return r
    except Exception as e:
        print(f" [!] Valkey connection failed: {e}")
        return None

# Global Valkey client instance
valkey_client = get_valkey_client()


@app.route('/api/v1/log_attendance', methods=['POST'])
def log_attendance():
    """Receives attendance data and publishes it instantly to the Valkey Stream."""
    global valkey_client

    # Check if Valkey client is available, try reconnecting if needed
    if valkey_client is None or not valkey_client.ping():
        valkey_client = get_valkey_client()
        if valkey_client is None:
             # Critical failure, cannot queue message
            return jsonify({'status': 'error', 'message': 'Queue service unavailable'}), 503

    try:
        data = request.json
        roll_no = data.get('roll_no')
        class_id = data.get('class_id')

        if not roll_no or not class_id:
            return jsonify({'status': 'error', 'message': 'Missing Roll No or Class ID'}), 400

        # The payload is stored as key-value pairs (must be bytes/strings in Redis)
        payload = {
            'roll_no': str(roll_no),
            'class_id': str(class_id),
            'timestamp': datetime.now().isoformat()
        }

        # XADD adds the message to the stream. '*' auto-generates the message ID.
        message_id = valkey_client.xadd(
            name=VALKEY_STREAM_NAME,
            fields=payload,
            maxlen=1000000, # Cap stream to 1 million entries
            approximate=True
        )
        print(f" [x] Sent message ID: {message_id.decode()} for Roll No: {roll_no}")

        # Respond immediately to the device for maximum speed
        return jsonify({'status': 'success', 'message': 'Attendance queued'}), 202

    except Exception as e:
        print(f" [!] Error during attendance processing: {e}")
        return jsonify({'status': 'error', 'message': 'Internal queueing error'}), 500

if __name__ == '__main__':
    # Run the producer service, perhaps on a separate port or machine from the consumer
    app.run(host='0.0.0.0', port=5000, debug=True)
