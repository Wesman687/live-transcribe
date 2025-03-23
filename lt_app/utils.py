import re
from .ai_processing import check_if_meaningful_with_ai
import lt_app.config as config

async def process_final_sentence(text, source, callback=None):
    """Finalize a transcription and store it in full history."""
    chat_history = None
    current_chat_history = []
    if source == "mic":
        config.mic_chat_history.append({"role": "user", "content": text})
        config.mic_pending_transcript = ""
        config.mic_buffer.clear()
        config.mic_speaking = False
        config.mic_eou_retries = 0
        current_chat_history = config.mic_chat_history
        config.last_mic_audio_time = None

    elif source == "system":
        config.system_chat_history.append({"role": "assistant", "content": text})
        config.system_pending_transcript = ""
        config.system_buffer.clear()
        config.system_speaking = False
        config.system_eou_retries = 0
        current_chat_history = config.system_chat_history
        config.last_system_audio_time = None
    elif source == "digital":
        config.digital_chat_history.append({"role": "user", "content": text})
        config.digital_pending_transcript = ""
        config.digital_buffer.clear()
        config.digital_speaking = False
        config.digital_eou_retries = 0
        current_chat_history = config.digital_chat_history
        config.last_digital_audio_time = None
    
    if callback:
        chat_history = await callback(text, source, current_chat_history)
        
    if chat_history:
        # You could store it globally or just pass it along if needed
        if source == "mic":
            config.mic_chat_history.append({"role": "assistant", "content": chat_history})
        elif source == "digital":
            config.digital_chat_history.append({"role": "assistant", "content": chat_history})
        elif source == "system":
            config.system_chat_history.append({"role": "assistant", "content": chat_history})

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

        
def lightly_clean_transcript(text: str) -> str:
    """Cleans up filler junk and formatting without altering meaning."""
    # Remove common Whisper filler junk
    text = re.sub(r"\b(thanks for (watching|listening|joining)|subscribe|click the bell)\b", "", text, flags=re.I)

    # Remove standalone polite closures like "Thank you." or "Thanks."
    text = re.sub(r"^(thank you|thanks)[.!]?$", "", text.strip(), flags=re.I)

    # Replace repeated filler punctuation
    text = re.sub(r"[.]{2,}", ".", text)   # convert "..." → "."
    text = re.sub(r"\s{2,}", " ", text)    # extra spaces
    text = re.sub(r"[,]{2,}", ",", text)

    # Optionally remove random symbols
    text = re.sub(r"[^\w\s.,!?'-]", "", text)

    return text.strip()