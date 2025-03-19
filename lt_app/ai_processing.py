import ollama
import lt_app.config as config


def check_if_meaningful_with_ai(text):
    """Use AI to determine if a short response is meaningful."""
    prompt = f"""
    You are analyzing a transcribed response from a job interview.

    The response is short (3-5 words).  
    Your task is to determine if it is a meaningful answer or just noise.

    **Meaningful Examples:**
    - "Yes, I have experience."
    - "I specialize in Python."
    - "I worked on a similar project."

    **Non-Meaningful Examples:**
    - "Yeah, uh huh."
    - "Hmmm, not sure."
    - "Okay, I see."

    Response:  
    "{text}"

    **Is this response meaningful? (Reply only "Yes" or "No")**
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])


    answer = response['message']['content'].strip().lower()
    return answer.startswith("yes")

def fix_transcription_with_ai(text):
    """Use AI to correct transcription errors while keeping key terms unchanged."""


    prompt = f"""
    **Role: AI Transcription Corrector**
    
    Your task is to **fix transcription errors** in spoken text **without changing meaning**.  
    The user has **an American accent**, and the transcription AI **sometimes mishears words**.

    **Rules:**
    - **Do NOT change words unless you are 100% sure they are incorrect.**
    - **Never assume a correction unless it's an obvious mistake.**
    - **The following words must remain unchanged:**
      {", ".join(config.WHITELIST_WORDS)}
    - **Maintain sentence structure.**
    - **Only correct actual misheard words. Do not rephrase the sentence.**

    **Example Fixes:**
    - "I use Redux to handle date management" → "I use Redux to handle state management."
    - "The time complexity is one o'clock" → "The time complexity is O(n)."
    - "Great bit for your honey" → "Great fit for your company."
    - **❌ INCORRECT:** "I use TypeScript" → "I use Django" (❌ WRONG)
    - **❌ INCORRECT:** "Your company" → "Your career path" (❌ WRONG)
    
    **Original Transcription:**  
    "{text}"

    **Return only the corrected text, keeping all whitelisted words unchanged.**  
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    fixed_text = response['message']['content'].strip()
    return fixed_text

