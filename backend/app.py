from flask import Flask, jsonify, request, send_file
from flask_sock import Sock
from flask_cors import CORS  # Enable CORS
import struct
import io
import wave
import speech_recognition as sr
from google import genai  # Gemini integration

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
sock = Sock(app)

# Global buffer to store incoming 16-bit audio samples
audio_buffer = []

# Initialize Gemini client (replace with your actual API key)
gemini_client = genai.Client(api_key="AIzaSyDyFSz_BSSZAIqFP_BXRZw02FjU99bX1do")

@sock.route('/ws')
def audio_socket(ws):
    print("WebSocket client connected.")
    while True:
        data = ws.receive()
        if data is None:
            break
        if isinstance(data, bytes):
            num_samples = len(data) // 2
            # Unpack the binary data into 16-bit signed integers (little-endian)
            samples = struct.unpack("<" + "h" * num_samples, data)
            audio_buffer.extend(samples)
    print("WebSocket client disconnected.")

@app.route('/save_audio')
def save_audio():
    if not audio_buffer:
        return jsonify({"error": "No audio data available."}), 400

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)       # Mono audio
        wav_file.setsampwidth(2)         # 16-bit samples (2 bytes per sample)
        wav_file.setframerate(16000)     # Sample rate
        for sample in audio_buffer:
            wav_file.writeframes(struct.pack("<h", sample))
    output.seek(0)
    return send_file(output, mimetype="audio/wav", as_attachment=True, download_name="recorded_audio.wav")

@app.route('/speech_to_text')
def speech_to_text():
    if not audio_buffer:
        return jsonify({"error": "No audio data available."}), 400

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        for sample in audio_buffer:
            wav_file.writeframes(struct.pack("<h", sample))
    output.seek(0)

    recognizer = sr.Recognizer()
    with sr.AudioFile(output) as source:
        audio_data = recognizer.record(source)
    try:
        # Use French for recognition (change language as needed)
        text = recognizer.recognize_google(audio_data, language="fr-FR")
        print("Transcription successful:", text)
        return jsonify({"transcription": text})
    except sr.UnknownValueError:
        error_msg = "Could not understand audio."
        print(error_msg)
        return jsonify({"transcription": error_msg})
    except sr.RequestError as e:
        error_msg = f"Speech recognition service error: {e}"
        print(error_msg)
        return jsonify({"transcription": error_msg})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided."}), 400

    # Build a prompt for Gemini – adjust as needed.
    prompt = f"Please provide a concise summary of the following text:\n\n{text}"
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",  # Adjust model name if needed
            contents=prompt
        )
        summary = response.text
        print("Summary generated:", summary)
        return jsonify({"summary": summary})
    except Exception as e:
        print("Error generating summary:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
