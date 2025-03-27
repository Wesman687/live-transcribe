
import base64
import time
import numpy as np
from .config import IGNORE_FIRST_SECONDS, MIN_VOLUME_THRESHOLD, NOISE_DURATION_THRESHOLD, SPEECH_THRESHOLD,  PAUSE_THRESHOLD, NOISE_DURATION_THRESHOLD
import lt_app.config as config
import audioop


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
        config.mic_chat_history = []
        config.system_chat_history = []
        config.digital_chat_history = []
        config.mic_pending_transcript = ""
        config.system_pending_transcript = ""
        config.digital_pending_transcript = ""
        time.sleep(2)
    else:
        print("🛑 Recording paused.")
        
def speech_detector(audio, source, speaking_callback=None):
    """Detect if speech starts or stops based on loudness threshold with continuous tracking."""
    current_time = time.time()
    if current_time - config.start_time < IGNORE_FIRST_SECONDS:
        return

    if audio > SPEECH_THRESHOLD:
        speaking_attr = f"{source}_speaking"
        last_audio_time_attr = f"last_{source}_audio_time"
        last_detected_time_attr = f"last_{source}_detected_time"

        # Get current speaking and last detected values
        speaking = getattr(config, speaking_attr, False)
        last_detected = getattr(config, last_detected_time_attr, 0)

        if not speaking and (current_time - last_detected > NOISE_DURATION_THRESHOLD):
            setattr(config, speaking_attr, True)
            setattr(config, last_audio_time_attr, current_time)
            if speaking_callback:
                speaking_callback(source, True)

        setattr(config, last_detected_time_attr, current_time)

def check_pause(source, speaking_callback=None):
    """Check if the audio source has been silent for too long."""
    current_time = time.time()
    last_audio_attr = f"last_{source}_audio_time"
    speaking_attr = f"{source}_speaking"

    last_audio_time = getattr(config, last_audio_attr, 0)
    speaking = getattr(config, speaking_attr, False)

    if speaking and (current_time - last_audio_time > PAUSE_THRESHOLD):
        print(f"🔕 {source.capitalize()} has been silent for too long. Pausing...")
        setattr(config, speaking_attr, False)
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
    
        
async def digital_stream(audio_data, speaking_callback=None):
    """Capture and process Twilio/VoIP digital streams separately from mic audio."""
    if config.RECORDING:
        try:
            # 🔹 Decode μ-law audio from Base64
            audio_mu_law_bytes = base64.b64decode(audio_data)
            # 🔹 Convert μ-law to PCM 16-bit
            pcm16_bytes = audioop.ulaw2lin(audio_mu_law_bytes, 2)
            # 🔹 Resample from 8 kHz to 16 kHz
            new_rate = 16000
            old_rate = 8000
            pcm16_16k_bytes, state = audioop.ratecv(pcm16_bytes, 2, 1, old_rate, new_rate, None)
            # 🔹 Convert PCM bytes to NumPy array (16-bit PCM)
            pcm16_np = np.frombuffer(pcm16_16k_bytes, dtype=np.int16)
            # 🔹 Normalize audio (Convert int16 PCM → float32 [-1.0 to 1.0])
            audio_float = pcm16_np.astype(np.float32) / 32768.0
            # 🔹 Compute Mean Volume
            mean_volume = np.mean(np.abs(audio_float))
            # 🔹 Ignore background noise based on volume threshold
            if mean_volume > config.MAX_DIGITAL_VOLUME_THRESHOLD:
                config.digital_buffer.append(audio_float.copy())  # Store audio in buffer
                config.last_digital_audio_time = time.time()

                # ✅ Use separate speech detection for Twilio
                speech_detector(mean_volume, "digital", speaking_callback)

            # 🔹 Check if user paused speaking
            check_pause("digital", speaking_callback)

        except Exception as e:
            print(f"❌ Error processing Twilio digital stream: {e}")
            
            
            
