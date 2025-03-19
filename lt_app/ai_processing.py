import ollama


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

    response = ollama.chat(model="deepseek", messages=[
        {"role": "user", "content": prompt}
    ])

    answer = response['message']['content'].strip().lower()
    print(f"🔍 AI Meaningfulness Check: {text} → {answer}")
    return answer.startswith("yes")

def fix_transcription_with_ai(text):
    """Use Mistral to correct minor transcription errors and fix misinterpreted words."""
    prompt = f"""
    **Role: AI Transcription Corrector**
    
    Your task is to **fix transcription errors** in spoken text.  
    The user has **an American accent**, and the transcription AI **sometimes misinterprets words**.

    **Common Fixes to Make:**
    - Correct **misheard words** (e.g., `"1 o'clock"` → `"O(n)"`)
    - Fix **misinterpreted technical terms** (e.g., `"date management"` → `"state management"`)
    - Correct **common interview-related transcription mistakes**
    - **Do not change sentence structure** unless absolutely necessary.

    **Example Corrections:**
    - "I use Redux to handle date management" → "I use Redux to handle state management."
    - "The time complexity is one o'clock" → "The time complexity is O(n)."
    - "Great bit for your honey" → "Great fit for your company."

    **Transcription to Fix:**  
    "{text}"

    **Return only the corrected text with no additional explanation.**  
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    fixed_text = response['message']['content'].strip()
    return fixed_text



async def process_recruiter_response(text):
    """Check if a recruiter's response is meaningful or just filler noise."""
    print("🤖 Checking if the recruiter's response is meaningful...")

    prompt = f"""
        **Role: Recruiter Evaluating a Candidate in a Job Interview**
        
        The following text is **spoken by a recruiter** after the candidate has responded.  
        You must determine **if it is a meaningful recruiter statement** or just a brief filler response.

        **Rules for Evaluation:**
        ✅ If the recruiter is **providing feedback, elaborating, or transitioning**, reply `"Yes"`.  
        ❌ If the recruiter **only says something brief with no meaningful context**, reply `"No"`.  

        **Examples of Meaningful Responses (`"Yes"`)**
        - "That's a great answer. Your experience with Kubernetes will be valuable for scaling our microservices."
        - "I appreciate that perspective! Can you tell me more about how you handled database migrations?"
        - "That makes sense. In our case, we had a similar issue when we moved from REST to GraphQL."

        **Examples of Filler/Noise (`"No"`)**
        - "Got it."
        - "Sounds good."
        - "Okay, thanks."
        - "Right, right."
        - "Understood."

        **Recruiter's Response to Evaluate:**  
        "{text}"

        **Is this a meaningful recruiter response? (Reply only with "Yes" or "No")**  
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    answer = response['message']['content'].strip().lower()
    print(f"🔍 AI Raw Response (Recruiter Response Check): {answer}")

    if answer.startswith("yes"):
        return True

    print("❌ Recruiter response is not finished.")
    return False


async def process_candidate_response(text):
    """Check if a candidate response is meaningful or just filler noise."""
    print("🤖 Checking if candidate response is meaningful...")

    prompt = f"""
        **Role: AI Evaluating a Job Interview Response**
        
        The following text is a **spoken response from a job candidate** during an interview.  
        You must determine **if it is a meaningful answer to a job interview question.**  

        **Rules for Evaluation:**
        ✅ If the response **conveys useful information**, reply `"Yes"`.  
        ❌ If the response **is just filler noise**, or a pause in a sentence, reply `"No"`.  

        **Examples of Meaningful Responses (`"Yes"`)**
        - "I have five years of experience with Python and React, primarily in full-stack development."
        - "I recently worked on a Kubernetes migration project to improve application scalability."
        - "The biggest challenge I faced was optimizing a real-time chat app to reduce WebSocket traffic."

        **Examples of Filler/Noise (`"No"`)**
        - "Uh huh, yeah, okay."
        - "Hmmm, let me think."
        - "I don't know, umm, yeah."
        - "Uh, yeah, it's like, you know, kind of hard to explain."
        - "I have five years of experience with python, " (incomplete sentence)

        **Candidate's Response to Evaluate:**  
        "{text}"

        **Is this a meaningful response? (Reply only with "Yes" or "No")**  
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    answer = response['message']['content'].strip().lower()
    print(f"🔍 AI Raw Response (Candidate): {answer}")

    if answer.startswith("yes"):
        return True

    print("❌ Response is not finished.")
    return False
