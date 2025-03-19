🎤 Live Transcribe

Real-time speech transcription using Whisper AI, optimized for Python.Supports custom backgrounds, AI processing, and GPU acceleration (CUDA).

📦 Installation

1️⃣ Install via PyPI (Default)

pip install live-transcribe

2️⃣ (Optional) Install CUDA-Optimized Version

If you have a GPU and want to enable CUDA support:

pip install torchaudio -f https://download.pytorch.org/whl/cu118.html

⚡ Quick Start

1️⃣ Run the Example

python examples/main.py

2️⃣ Use as a Library

You can integrate live-transcribe into your own Python scripts.

import asyncio
from lt_app.transcriber import transcribe_audio

async def custom_callback(transcript, source):
    print(f"Transcript from {source}: {transcript}")

asyncio.run(transcribe_audio(callback=custom_callback))

🛠️ Features

✅ Real-time transcription using Whisper AI✅ AI-powered sentence correction (via ollama)✅ Customizable background noise filtering✅ Supports GPU acceleration (CUDA)✅ Use as a standalone CLI or inside Python projects✅ Toggle recording on/off using spacebar✅ Capture both microphone and system audio streams

💩 Configuration

You can customize settings by modifying config.py or loading from YAML.

Example YAML Configuration

SAMPLE_RATE: 16000
MIN_PAUSE_THRESHOLD: 2
MAX_PAUSE_THRESHOLD: 4
SPEECH_THRESHOLD: 1400
CUDA_ENABLED: true

🖥️ Running Without main.py

If you don't want to use the built-in main.py, you can create a custom implementation.

Example: Transcribing Audio from an API Call

from lt_app.transcriber import transcribe_audio

async def api_transcription():
    print("🎤 Starting Live Transcription...")
    await transcribe_audio(callback=print)

asyncio.run(api_transcription())

🔊 Handling Audio Streams & Recording Control

1️⃣ Toggle Recording (Start/Stop)

By default, the program starts in a paused state. You can start/stop recording by pressing spacebar:

from lt_app.audio import toggle_recording

toggle_recording()  # Start or stop recording

2️⃣ Managing Audio Streams

The transcription system captures both microphone and system (loopback) audio:

import sounddevice as sd
from lt_app.audio import mic_callback, system_callback

mic_stream = sd.InputStream(
    samplerate=16000, channels=1, callback=mic_callback, dtype="int16", device=1
)
system_stream = sd.InputStream(
    samplerate=16000, channels=1, callback=system_callback, dtype="int16", device=3
)

mic_stream.start()
system_stream.start()

If you need to stop the audio streams safely:

mic_stream.close()
system_stream.close()

⚙️ Advanced Setup

Check if CUDA is Enabled

Run the following inside Python:

import torch
print("CUDA Available:", torch.cuda.is_available())

If False, install CUDA-optimized torchaudio:

pip install torchaudio -f https://download.pytorch.org/whl/cu118.html

🛠️ Development & Contributions

1️⃣ Clone the Repository

git clone https://github.com/yourgithub/live-transcribe.git
cd live-transcribe

2️⃣ Install in Development Mode

pip install -e .

3️⃣ Run Tests

pytest tests/

🐜 License

This project is licensed under the MIT License.

📞 Need Help?

GitHub Issues: https://github.com/yourgithub/live-transcribe/issues

Contact: your_email@example.com

🚀 Enjoy real-time transcription with live-transcribe! 🚀

