import logging
from flask import Flask, request, jsonify
import requests
import binascii
import gzip
import json
from io import BytesIO

app = Flask(__name__)

PARSEABLE_ENDPOINT = "http://localhost:8000/api/v1/logstream/otelalloydemo"
AUTH_HEADER = "Basic YWRtaW46YWRtaW4="
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/v1/logs', methods=['POST'])
def receive_logs():
    try:
        raw_data = request.data
        logger.info(f"Raw data received: {binascii.hexlify(raw_data).decode('utf-8')}")

        # Decompress the gzip data
        with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
            decompressed_data = f.read()
        
        # Convert decompressed data to JSON
        log_data = json.loads(decompressed_data.decode('utf-8'))
        logger.info(f"Decompressed and parsed JSON data: {log_data}")

        headers = {
            "Authorization": AUTH_HEADER,
            "Content-Type": "application/json",
        }

        # Forward the log data to the parseable endpoint with headers
        response = requests.post(PARSEABLE_ENDPOINT, json=log_data, headers=headers)

        if response.status_code == 200:
            logger.info("Logs forwarded successfully")
            return jsonify({"status": "Logs forwarded successfully"}), 200
        else:
            logger.error(f"Failed to forward logs, status code: {response.status_code}")
            return jsonify({"error": "Failed to forward logs"}), response.status_code

    except Exception as e:
        logger.exception("An error occurred while processing logs")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3004)
