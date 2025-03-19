from .ai_processing import check_if_meaningful_with_ai
import time
import lt_app.config as config


def process_final_sentence(text, is_mic):
    """Finalize a transcription and store it in full history."""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if is_mic:
        config.last_transcription_mic = ""
        config.mic_buffer.clear()
        config.mic_speaking = False
        print(f"Me: {text}")

        # ✅ Store in full transcript
        config.full_transcription.append(f"[{timestamp}] Me: {text}")
    else:
        config.last_transcription_system = ""
        config.system_buffer.clear()
        config.system_speaking = False
        print(f"Recruiter: {text}")

        # ✅ Store in full transcript
        config.full_transcription.append(f"[{timestamp}] Recruiter: {text}") 


def is_meaningful_text(text):
    """Detect if the transcribed text is meaningful or just filler noise."""
    cleaned_text = text.strip().lower()
    words = cleaned_text.split()
    if len(words) > 5:
        return True
    print(f"DEBUG: words={words}, length={len(words)}")  # 🔥 Check word count
    junk_responses = {"uh", "uh huh", "hmm", "yeah", "okay", "um", "huh", "hmm...", "...", "thanks for watching!"}    

    # ✅ If it's in the junk list, it's meaningless
    if cleaned_text in junk_responses:
        return False
    
    if len(words) < 3:
        return False
    
    return check_if_meaningful_with_ai(text)

        

