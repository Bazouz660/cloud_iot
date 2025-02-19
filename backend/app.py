from flask import Flask, send_file, jsonify
from flask_sock import Sock
import struct
import io
import wave

app = Flask(__name__)
sock = Sock(app)

# Global buffer to store incoming 16-bit samples
audio_buffer = []

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
            print(f"Received {num_samples} samples. Total stored: {len(audio_buffer)}")
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
        # Write audio samples to WAV file
        for sample in audio_buffer:
            wav_file.writeframes(struct.pack("<h", sample))
    output.seek(0)
    return send_file(output, mimetype="audio/wav", as_attachment=True, download_name="recorded_audio.wav")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
