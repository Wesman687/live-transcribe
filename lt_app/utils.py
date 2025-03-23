from .ai_processing import check_if_meaningful_with_ai
import lt_app.config as config


async def process_final_sentence(text, source, callback=None):
    """Finalize a transcription and store it in full history."""
    if callback:
        await callback(text, source)
    if source == "mic":
        config.mic_buffer.clear()
        config.mic_speaking = False

    elif source == "system":
        config.system_buffer.clear()
        config.system_speaking = False
    elif source == "digital":
        config.digital_buffer.clear()
        config.digital_speaking = False

def is_meaningful_text(text):
    """Detect if the transcribed text is meaningful or just filler noise."""
    if config.MEANINGFUL_ON:
        cleaned_text = text.strip().lower()
        words = cleaned_text.split()
        if len(words) > config.MAX_MEANINGFUL_WORDS:
            return True
        
        # ✅ If it's in the junk list, it's meaningless
        if cleaned_text in config.JUNK_RESPONSES:
            return False
        
        if len(words) < config.MIN_MEANINGFUL_WORD:
            return False
        
        return check_if_meaningful_with_ai(text)

        
