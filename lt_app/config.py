

import time


SAMPLE_RATE = 16000

MIN_PAUSE_THRESHOLD = 2
MAX_PAUSE_THRESHOLD = 4

SPEECH_THRESHOLD = 1400  # 🔥 Increase to ignore background noise
MIN_VOLUME_THRESHOLD = 1400  # 🔥 Ignore very quiet sounds
NOISE_DURATION_THRESHOLD = 1  # 🔥 Speech must last 0.7s to be detected
IGNORE_FIRST_SECONDS = 1.5  # 🔥 Ignore small noises right after unpausing

# ✅ Device Configuration (Double-check indexes with `sd.query_devices()`)
MIC_DEVICE = 12  # CHANGE THIS TO YOUR MIC ID
SYSTEM_DEVICE = 34  # CHANGE THIS TO YOUR SYSTEM AUDIO ID

 # 🔥 Maximum pause threshold
PAUSE_THRESHOLD = 1.7  # 🔥 If no speech detected for 3s, consider it a break

        
NOISE_WORDS = {"uh", "uhh", "uh huh", "hmm", "hmmm", "okay", "ok", "right", "yeah", "yep", "yup"}

CHANNELS = 1
RECORDING = False  # ✅ Start in paused mode
full_transcription = []

# ✅ Audio Buffers & State
mic_buffer = []
system_buffer = []
last_mic_detected_time = time.time()
last_system_detected_time = time.time()
last_mic_audio_time = time.time()
last_system_audio_time = time.time()
start_time = time.time()  # Track when recording starts
last_transcription_mic = ""
last_transcription_system = ""

mic_speaking = False
system_speaking = False
