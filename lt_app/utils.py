from .ai_processing import check_if_meaningful_with_ai
import time
import lt_app.config as config


async def process_final_sentence(text, source, callback=None):
    """Finalize a transcription and store it in full history."""
    if callback:
        await callback(text, source)
    if source == "mic":
        config.last_transcription_mic = ""
        config.mic_buffer.clear()
        config.mic_speaking = False

    elif source == "system":
        config.last_transcription_system = ""
        config.system_buffer.clear()
        config.system_speaking = False
    elif source == "digital":
        config.last_transcription_digital = ""
        config.digital_buffer.clear()
        config.digital_speaking = False

def is_meaningful_text(text):
    """Detect if the transcribed text is meaningful or just filler noise."""
    cleaned_text = text.strip().lower()
    words = cleaned_text.split()
    if len(words) > 5:
        return True
     
    # ✅ If it's in the junk list, it's meaningless
    if cleaned_text in config.JUNK_RESPONSES:
        return False
    
    if len(words) < 3:
        return False
    
    return check_if_meaningful_with_ai(text)

        

