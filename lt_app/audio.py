
import time
import numpy as np
from .config import IGNORE_FIRST_SECONDS, MIN_VOLUME_THRESHOLD, NOISE_DURATION_THRESHOLD, SPEECH_THRESHOLD,  PAUSE_THRESHOLD, NOISE_DURATION_THRESHOLD
import lt_app.config as config


def toggle_recording():
    """Toggle recording when spacebar is pressed."""

    config.RECORDING = not config.RECORDING
    if config.RECORDING:
        print("🎤 Recording started...")
        config.mic_buffer.clear()
        config.system_buffer.clear()
        config.mic_speaking = False  # ✅ Reset speaking state when resuming
        config.system_speaking = False
        config.start_time = time.time()
        time.sleep(2)
    else:
        print("🛑 Recording paused.")
        
def speech_detector(audio, source):
    """Detect if speech starts or stops based on loudness threshold with continuous tracking."""
    current_time = time.time()
    if current_time - config.start_time < IGNORE_FIRST_SECONDS:
        return  

    if audio > SPEECH_THRESHOLD:
        if source == "mic":
            if not config.mic_speaking or (current_time - config.last_mic_detected_time > NOISE_DURATION_THRESHOLD):
                config.mic_speaking = True
                config.last_mic_audio_time = current_time
                print(f"🎙️ Mic Speech detected! (Volume: {audio})")
            config.last_mic_detected_time = current_time  # 🔹 Update last speech detection time
        else:
            if not config.system_speaking or (current_time - config.last_system_detected_time > NOISE_DURATION_THRESHOLD):
                config.system_speaking = True
                config.last_system_audio_time = current_time
                print(f"🔊 System Speech detected! (Volume: {audio})")
            config.last_system_detected_time = current_time  # 🔹 Update last speech detection time

def check_pause(source):
    """Check if the audio source has been silent for too long."""
    current_time = time.time()
    last_audio_time = config.last_mic_audio_time if source == "mic" else config.last_system_audio_time
    speaking = config.mic_speaking if source == "mic" else config.system_speaking
    if speaking and (current_time - last_audio_time > PAUSE_THRESHOLD):
        print("🔇 Silence detected. Waiting for new speech...")
        if source == "mic":
            config.mic_speaking = False
        else:
            config.system_speaking = False


def mic_callback(indata, frames, _, status):
    """Capture microphone audio when recording is enabled, ignoring very low volume."""
    if config.RECORDING:
        max_amplitude = np.max(np.abs(indata))
        if max_amplitude > MIN_VOLUME_THRESHOLD:  # Ignore background noise
            print("send to speech")
            config.mic_buffer.append(indata.copy())
            config.last_mic_audio_time = time.time()
            speech_detector(max_amplitude, 'mic')
        check_pause("mic")
        
def system_callback(indata, frames, _, status):
    """Capture system audio when recording is enabled, ignoring very low volume."""
    if config.RECORDING:
        max_amplitude = np.max(np.abs(indata))
        if max_amplitude > MIN_VOLUME_THRESHOLD:  # Ignore background noise
            config.system_buffer.append(indata.copy())
            config.last_system_audio_time = time.time()
            speech_detector(max_amplitude, 'system')
        check_pause("system")