from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import wave
import struct
import io

app = Flask(__name__)
CORS(app)

# Global buffer to store 16-bit audio samples (as integers)
audio_buffer = []

@app.route('/api/audio', methods=['POST'])
def process_audio():
    # Read binary data from the request
    raw_data = request.get_data()
    # Convert the binary data to a list of 16-bit samples
    num_samples = len(raw_data) // 2
    samples = list(struct.unpack("<" + "h"*num_samples, raw_data))

    # Append to your global audio buffer
    audio_buffer.extend(samples)
    print(f"Received {num_samples} samples. Total stored: {len(audio_buffer)}")

    return jsonify({"status": "ok", "samples_received": num_samples})


@app.route('/api/save_audio', methods=['GET'])
def save_audio():
    if not audio_buffer:
        return jsonify({"status": "No audio data available."}), 400

    # Create an in-memory WAV file
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)       # Mono audio
        wav_file.setsampwidth(2)         # 16-bit samples (2 bytes)
        wav_file.setframerate(16000)     # Sample rate (Hz)
        # Write each sample as little-endian 16-bit
        for sample in audio_buffer:
            wav_file.writeframes(struct.pack("<h", int(sample)))
    output.seek(0)
    # Optionally, clear the buffer after saving:
    # audio_buffer.clear()
    return send_file(output, mimetype="audio/wav", as_attachment=True, download_name="recorded_audio.wav")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
