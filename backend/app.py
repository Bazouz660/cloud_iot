from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
latest_summary = "No summary yet."

@app.route('/api/audio', methods=['POST'])
def process_audio():
    global latest_summary
    data = request.get_json()
    mic_value = data.get('micValue', 0)

    # Simulate processing: generate a daily summary based on the mic value
    latest_summary = f"Simulated daily summary based on mic value: {mic_value}"
    print(f"Processed data: {latest_summary}")

    return jsonify({"summary": latest_summary})

@app.route('/api/summary', methods=['GET'])
def get_summary():
    return jsonify({"summary": latest_summary})

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so the ESP32 can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
