from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

latest_summary = "No summary yet."
mic_values = []

# Initialize the Google generative AI client with your API key.
client = genai.Client(api_key="AIzaSyDyFSz_BSSZAIqFP_BXRZw02FjU99bX1do")

@app.route('/api/audio', methods=['POST'])
def process_audio():
    global latest_summary
    data = request.get_json()
    mic_value = data.get('micValue', 0)

    # Append the new mic value to our list
    mic_values.append(mic_value)
    print(f"Received mic value: {mic_value}")

    # Check if we've accumulated enough values to generate a summary.
    if len(mic_values) >= 5:
        # Build a prompt from the mic values. Here we treat the numbers as simulated noise levels.
        prompt = "The following are simulated microphone readings (noise levels) recorded throughout the day: " + \
                 ", ".join(str(v) for v in mic_values) + \
                 ". Based on these readings, provide a brief summary of the user's day."

        try:
            # Call the Gemini 2.0 Flash model
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            latest_summary = response.text
            print(f"Generated summary: {latest_summary}")
        except Exception as e:
            latest_summary = "Error generating AI summary."
            print(f"Error calling AI model: {e}")

        # Clear the list after generating the summary
        mic_values.clear()
    else:
        # If not enough data, update a placeholder message.
        latest_summary = f"Collected {len(mic_values)} microphone values so far."

    return jsonify({"summary": latest_summary})

@app.route('/api/summary', methods=['GET'])
def get_summary():
    return jsonify({"summary": latest_summary})

if __name__ == '__main__':
    # Run on all interfaces so the ESP32 can connect.
    app.run(host='0.0.0.0', port=5000, debug=True)
