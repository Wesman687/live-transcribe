
import numpy as np
import asyncio
import time
from faster_whisper import WhisperModel

from .ai_processing import fix_transcription_with_ai, process_candidate_response, process_recruiter_response
from .config import MAX_PAUSE_THRESHOLD, MIN_PAUSE_THRESHOLD
from .utils import is_meaningful_text, process_final_sentence
import lt_app.config as config

last_transcription_mic_time = time.time()
last_transcription_system_time = time.time()

# ✅ Whisper Model Initialization
whisper_model = WhisperModel("medium", device="cuda", compute_type="float16")


async def transcribe_audio():
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
                if check_time >= MIN_PAUSE_THRESHOLD:  # Ensure enough pause
                    tasks.append(handle_transcription("mic", config.mic_buffer, check_time))

            # ✅ Handle System Buffer if it exists
            if config.system_buffer:
                last_audio_time = config.last_system_audio_time
                check_time = current_time - last_audio_time
                if check_time >= MIN_PAUSE_THRESHOLD:  # Ensure enough pause
                    tasks.append(handle_transcription("system", config.system_buffer, check_time))

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
        speaker_label = "Me" if source == "mic" else "Recruiter"
        if source == "mic":
            config.last_transcription_mic = ""
        else:
            config.last_transcription_system = ""

        # 🔥 Transcribe with Whisper
        segments, _ = whisper_model.transcribe(audio_data)
        transcript = " ".join(segment.text for segment in segments).strip()
        if not is_meaningful_text(transcript):
            print(f"❌ {speaker_label} said meaningless text, ignoring transcript.")
            return None  # ✅ Return nothing to discard the junk
        transcript = fix_transcription_with_ai(transcript)
        return transcript

    except Exception as e:
        print(f"❌ Transcription error ({source}): {e}")
        return None

async def handle_transcription(source, buffer, check_time):
    """Process transcription for mic or system audio independently."""
    global  last_transcription_mic_time, last_transcription_system_time
    
    transcript = process_transcription(source, buffer)
    if not transcript:
        last_transcript = config.last_transcription_mic if source == "mic" else config.last_transcription_system
                
        # If there's no last transcript, there's nothing to process, so return
        if not last_transcript:
            return
                
        # ✅ If MAX_PAUSE_THRESHOLD is exceeded, forcefully process the last known transcription
        if check_time >= MAX_PAUSE_THRESHOLD:
            print(f"⏳ MAX_PAUSE_THRESHOLD reached ({check_time:.2f}s) with no new transcript. Processing last statement.")
            process_final_sentence(last_transcript, source == "mic")  # ✅ Process last transcription
            return
                
    # ✅ Combine transcript with previous transcription before sending
    if source == "mic":
        transcript = f"{config.last_transcription_mic} {transcript}".strip() if config.last_transcription_mic else transcript
        config.last_transcription_mic = transcript
        last_transcription_mic_time = time.time()
    else:
        transcript = f"{config.last_transcription_system} {transcript}".strip() if config.last_transcription_system else transcript
        config.last_transcription_system = transcript
        last_transcription_system_time = time.time()

    print(f"📝 {'Me' if source == 'mic' else 'Recruiter'}: {transcript}")

    processed = None

    if source == "mic": 
        processed = await process_candidate_response(transcript) 
    else:
        processed = await process_recruiter_response(transcript)   
                
    if not processed:
        print(f"⚠️ AI didn't confirm {source} response as meaningful. Checking for forced processing...")
        
    if processed:
        if source == "mic":
            process_final_sentence(transcript, True)
            config.mic_buffer.clear()
        else:
            process_final_sentence(transcript, False)
            config.system_buffer.clear()       
        
        
