
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
        config.digital_buffer.clear()
        config.digital_speaking = False
        config.mic_speaking = False  # ✅ Reset speaking state when resuming
        config.system_speaking = False
        config.start_time = time.time()
        time.sleep(2)
    else:
        print("🛑 Recording paused.")
        
def speech_detector(audio, source, speaking_callback=None):
    """Detect if speech starts or stops based on loudness threshold with continuous tracking."""
    current_time = time.time()
    if current_time - config.start_time < IGNORE_FIRST_SECONDS:
        return  

    if audio > SPEECH_THRESHOLD:
        if source == "mic":
            if not config.mic_speaking or (current_time - config.last_mic_detected_time > NOISE_DURATION_THRESHOLD):
                config.mic_speaking = True
                config.last_mic_audio_time = current_time
                if speaking_callback:
                    speaking_callback(source, True)
            config.last_mic_detected_time = current_time  # 🔹 Update last speech detection time
        elif source == "system":
            if not config.system_speaking or (current_time - config.last_system_detected_time > NOISE_DURATION_THRESHOLD):
                config.system_speaking = True
                config.last_system_audio_time = current_time
                if speaking_callback:
                    speaking_callback(source, True)
            config.last_system_detected_time = current_time  # 🔹 Update last speech detection time
        else:
            if not config.digital_speaking or (current_time - config.last_digital_detected_time > NOISE_DURATION_THRESHOLD):
                config.digital_speaking = True
                config.last_digital_audio_time = current_time
                if speaking_callback:
                    speaking_callback(source, True)
            config.last_digital_detected_time = current_time

def check_pause(source, speaking_callback=None):
    """Check if the audio source has been silent for too long."""
    current_time = time.time()
    last_audio_time = config.last_mic_audio_time if source == "mic" else config.last_system_audio_time
    speaking = config.mic_speaking if source == "mic" else config.system_speaking
    if speaking and (current_time - last_audio_time > PAUSE_THRESHOLD):
        if source == "mic":
            config.mic_speaking = False
        else:
            config.system_speaking = False
        if speaking_callback:
            speaking_callback(source, False)


def mic_callback(indata, frames, _, status, speaking_callback=None):
    """Capture microphone audio when recording is enabled, ignoring very low volume."""
    if config.RECORDING:
        max_amplitude = np.max(np.abs(indata))
        if max_amplitude > MIN_VOLUME_THRESHOLD:  # Ignore background noise
            config.mic_buffer.append(indata.copy())
            config.last_mic_audio_time = time.time()
            speech_detector(max_amplitude, 'mic', speaking_callback)
        check_pause("mic", speaking_callback)
        
def system_callback(indata, frames, _, status, speaking_callback=None):
    """Capture system audio when recording is enabled, ignoring very low volume."""
    if config.RECORDING:
        max_amplitude = np.max(np.abs(indata))
        if max_amplitude > MIN_VOLUME_THRESHOLD:  # Ignore background noise
            config.system_buffer.append(indata.copy())
            config.last_system_audio_time = time.time()
            speech_detector(max_amplitude, 'system', speaking_callback)
        check_pause("system", speaking_callback)
    
    
        
def digital_stream(audio_data, speaking_callback=None):
        """Capture and process Twilio/VoIP digital streams separately from mic audio."""
        if config.RECORDING:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # ✅ Compute Mean Volume Level (to detect silence)
        mean_volume = np.mean(np.abs(audio_array))      
        if mean_volume > config.MIN_VOLUME_THRESHOLD:  # Ignore background noise
            audio_array = audio_array.reshape(-1, config.CHANNELS)
            config.digital_buffer.append(audio_array.copy())
            config.last_digital_audio_time = time.time()

            # ✅ Use separate detection logic for Twilio
            speech_detector(mean_volume, "digital", speaking_callback)
        check_pause("digital", speaking_callback)