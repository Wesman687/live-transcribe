
import numpy as np
import asyncio
import time
from faster_whisper import WhisperModel

from .ai_processing import fix_transcription_with_ai
from .config import MAX_PAUSE_THRESHOLD
from .utils import is_meaningful_text, process_final_sentence
import lt_app.config as config



# ✅ Initialize the Whisper Model with optimized settings
whisper_model = WhisperModel(config.MODEL_SIZE, device=config.DEVICE, compute_type=config.COMPUTE_TYPE)


async def transcribe_audio(callback=None):
    """Continuously transcribe audio and detect sentence boundaries."""
    try:
        while True:
            if not config.RECORDING:
                await asyncio.sleep(0.5)
                continue  # 🔹 Skip processing when paused
            await asyncio.sleep(1)  # 🔥 Adjust for responsiveness
            current_time = time.time()

            # ✅ Process Mic and System Audio **at the same time**
            tasks = []

            # ✅ Handle Mic Buffer if it exists
            if config.mic_buffer:
                last_audio_time = config.last_mic_audio_time
                check_time = current_time - last_audio_time
                if check_time >= MAX_PAUSE_THRESHOLD:  # Ensure enough pause
                    tasks.append(handle_transcription("mic", config.mic_buffer, callback))

            # ✅ Handle System Buffer if it exists
            if config.system_buffer:
                last_audio_time = config.last_system_audio_time
                check_time = current_time - last_audio_time
                if check_time >= MAX_PAUSE_THRESHOLD:  # Ensure enough pause
                    tasks.append(handle_transcription("system", config.system_buffer, callback))

            # ✅ Run both transcriptions **at the same time**
            if tasks:
                await asyncio.gather(*tasks)
                
    except Exception as e:
        print(f"❌ Transcription loop error: {e}")


# ✅ Mic & System Audio Settings

def process_transcription(source, buffer):
    """Process and transcribe audio from a given buffer."""
    try:
        audio_data = np.concatenate(buffer, axis=0).flatten()
        buffer.clear()  # ✅ Clear the buffer after processing

        if np.max(np.abs(audio_data)) == 0:
            return None  # 🔹 Avoid division by zero errors

        # ✅ Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        if source == "mic":
            config.last_transcription_mic = ""
        else:
            config.last_transcription_system = ""

        # 🔥 Transcribe with Whisper
        segments, _ = whisper_model.transcribe(audio_data)
        transcript = " ".join(segment.text for segment in segments).strip()
        if not is_meaningful_text(transcript):
            return None  # ✅ Return nothing to discard the junk
        transcript = fix_transcription_with_ai(transcript)
        return transcript

    except Exception as e:
        print(f"❌ Transcription error ({source}): {e}")
        return None

async def handle_transcription(source, buffer, callback=None):
    """Process transcription for mic or system audio independently."""
    
    transcript = process_transcription(source, buffer)    
    if not transcript:
        last_transcript = config.last_transcription_mic if source == "mic" else config.last_transcription_system
                
        # If there's no last transcript, there's nothing to process, so return
        if not last_transcript:
            return
                
    if source == "mic":
        transcript = f"{config.last_transcription_mic} {transcript}".strip() if config.last_transcription_mic else transcript
        config.last_transcription_mic = transcript
        config.last_transcription_mic_time = time.time()
    else:
        transcript = f"{config.last_transcription_system} {transcript}".strip() if config.last_transcription_system else transcript
        config.last_transcription_system = transcript
        config.last_transcription_system_time = time.time()

    await process_final_sentence(transcript, source == "mic", callback)
        
        
