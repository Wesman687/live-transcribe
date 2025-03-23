
import numpy as np
import asyncio
import time
from faster_whisper import WhisperModel

from lt_app.turn_detector import get_turn_probability

from .ai_processing import fix_transcription_with_ai
from .config import MAX_PAUSE_THRESHOLD
from .utils import is_meaningful_text, lightly_clean_transcript, process_final_sentence
import lt_app.config as config
import traceback

whisper_model = WhisperModel(
    config.MODEL_SIZE,  # e.g. "large-v3"
    device=config.DEVICE,  # e.g. "cuda" or "cpu"
    compute_type=config.COMPUTE_TYPE  # e.g. "float16" or "int8"
)
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
            if config.digital_buffer:
                last_audio_time = config.last_digital_audio_time
                check_time = current_time - last_audio_time
                if check_time >= MAX_PAUSE_THRESHOLD:  # Ensure enough pause
                    tasks.append(handle_transcription("digital", config.digital_buffer, callback))
            if not config.mic_speaking and config.last_mic_audio_time and time.time() - config.last_mic_audio_time >= config.MAX_SILENCE_TIMEOUT and config.mic_pending_transcript.strip():
                print(f"[DEBUG] Time since mic audio: {time.time() - config.last_mic_audio_time:.2f}s")
                print(f"[DEBUG] Mic speaking: {config.mic_speaking}")
                print("⏰ Mic audio timeout reached — forcing transcription")
                await process_final_sentence("mic", config.mic_pending_transcript, callback)
                config.mic_pending_transcript = ""

            if not config.system_speaking and config.last_system_audio_time  and time.time() - config.last_system_audio_time >= config.MAX_SILENCE_TIMEOUT and config.system_pending_transcript.strip():
                print("⏰ System audio timeout reached — forcing transcription")
                await process_final_sentence("system", config.system_pending_transcript, callback)
                config.system_pending_transcript = ""

            if config.digital_speaking and config.last_digital_audio_time and time.time() - config.last_digital_audio_time >= config.MAX_SILENCE_TIMEOUT and config.digital_pending_transcript.strip():
                print("⏰ Digital audio timeout reached — forcing transcription")
                await process_final_sentence("digital", config.digital_pending_transcript, callback)
                config.digital_pending_transcript = ""
                
            if tasks:
                await asyncio.gather(*tasks)
                
    except Exception as e:
        print(f"❌ Transcription loop error: {e}")
        traceback.print_exc()


async def process_transcription(source, buffer):
    """Process and transcribe audio from a given buffer."""
    try:
        current_time = time.time()
        if source == "mic" and current_time - config.last_mic_eou_attempt < config.MIN_EOU_INTERVAL:
            print("🔁 Skipping mic transcription — debounce in effect.")
            return None
        if source == "system" and current_time - config.last_system_eou_attempt < config.MIN_EOU_INTERVAL:
            print("🔁 Skipping system transcription — debounce in effect.")
            return None
        if source == "digital" and current_time - config.last_digital_eou_attempt < config.MIN_EOU_INTERVAL:
            print("🔁 Skipping digital transcription — debounce in effect.")
            return None
        
        audio_data = np.concatenate(buffer, axis=0).flatten()
        buffer.clear()  # ✅ Clear the buffer after processing

        if np.max(np.abs(audio_data)) == 0:
            return None  # 🔹 Avoid division by zero errors        
        
        # ✅ Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        # 🔥 Transcribe with Whisper
        segments, info = whisper_model.transcribe(audio_data, language="en")
        transcript = " ".join(segment.text for segment in segments).strip()  
        if not isinstance(transcript, str):
            print("⚠️ Transcript is not a string, skipping.")
            return None      
        temp_chat_history = []
        pending_transcript = lightly_clean_transcript(transcript)
        if source == "mic":
            config.mic_pending_transcript += " " + pending_transcript
            pending_transcript = config.mic_pending_transcript
            temp_chat_history = config.mic_chat_history[-19:] + [{"role": "user", "content": pending_transcript}]
        elif source == "system":
            config.system_pending_transcript += " " + pending_transcript
            pending_transcript = config.system_pending_transcript
            temp_chat_history = config.system_chat_history[-19:] + [{"role": "assistant", "content": pending_transcript}]
        else:
            config.digital_pending_transcript += " " + pending_transcript
            pending_transcript = config.digital_pending_transcript
            temp_chat_history = config.digital_chat_history[-19:] + [{"role": "user", "content": pending_transcript}]
            
        if not isinstance(pending_transcript, str):
            print("⚠️ Pending transcript is not a string, skipping.")
            return None
        if not is_meaningful_text(pending_transcript):
            return None  # ✅ Return nothing to discard the junk
        eou_prob = None
        loop = asyncio.get_event_loop()
        try:
             eou_prob = await loop.run_in_executor(None, get_turn_probability, temp_chat_history)
        except Exception as e:
            print(f"Error calculating EOU probability: {e}")
            return None
        if eou_prob is None:
            print("⚠️ EOU probability is None, skipping.")
            return None
        print(f"Temp Chat History: {temp_chat_history}")
        print(f"🔍 EOU Probability: {eou_prob}")
        if eou_prob > config.EOU_THRESHOLD:
            print("✅ User likely finished speaking, processing intent...")           
        else:
            print("⏳ Not confident it's finished. Waiting for more...")
            force_transcribe = False
            # Update debounce timestamp
            if source == "mic":
                config.mic_eou_retries += 1
                config.last_mic_eou_attempt = current_time
                if config.mic_eou_retries > config.MAX_EOU_RETRIES:
                    force_transcribe = True
            elif source == "system":
                config.system_eou_retries += 1
                config.last_system_eou_attempt = current_time
                if config.system_eou_retries > config.MAX_EOU_RETRIES:
                    force_transcribe = True
            elif source == "digital":
                config.digital_eou_retries += 1
                config.last_digital_eou_attempt = current_time
                if config.digital_eou_retries > config.MAX_EOU_RETRIES:
                    force_transcribe = True
            if not force_transcribe:
                return None    
        if config.FIX_TRANSCRIPTION:
            final_transcript = fix_transcription_with_ai(pending_transcript)         
        
        
        return final_transcript

    except Exception as e:
        print(f"❌ Transcription error ({source}): {e}")
        return None

async def handle_transcription(source, buffer, callback=None):
    """Process transcription for mic or system audio independently."""
        
    transcript = await process_transcription(source, buffer)   
    if transcript is not None:             
        await process_final_sentence(transcript, source, callback)
        
        
