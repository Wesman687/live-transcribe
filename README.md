### **🎤 Live Transcribe** 

Keep in mind this is ran locally with calls to several AI models, this will take at least modest resources to run reliably.
If you don't have a faster computer, you may want to consider API transcriptions such as OPENAI or Google Speec to text.

I have found Faster-Whisper to be a bit more reliable, but it does run quite a bit of resources.

This is a project i'm working on to work with my transcription apps.  The higher the model is the better your accuracy is, I have
found that using the transcription fixes can provide mix results, but if you make it application specific it can be very reliable.

Whisper like's to throw in Thank you, Thanks for Watching randomly, so we have taken out those phrases, so keep in mind "Thank You"
Will not transcribe, this is intentional.  

The code probably needs to be refactored and can be coded a bit better, there might be slight bugs as well.  As I said I am working on other projects
and testing in between, so please report any bugs or improvements you might find.  It would be a great help. 

Currently this just supports Microphone/System sounds sound device, it also has a twilio feed named digital_stream (will probably rename this later).
I will probably add in a real digital_stream later on for like frontend programs that record and send to the backend/server.  (Only so much time in the day)

If you are having problems getting the speech detected, it is most likely the Volume that starts the speech activity.  This is represented in these 2 variables
MAX_DIGITAL_VOLUME_THRESHOLD = .05  #Volume to detect speech
SPEECH_THRESHOLD = 1800   #Audio to detect speech

You can add a print statement on the callback right here, and speak/send sound, then it will show you what volume your device is runnig on, then adjust accordingly.

        max_amplitude = np.max(np.abs(indata))
        print(max_amplited)
        if max_amplitude > MIN_VOLUME_THRESHOLD:  # Ignore background noise
            config.mic_buffer.append(indata.copy())

This is a crucial setting bc you get a lot of background noise and ambient noices, so without this being set just right, the transcript will just keep running the loop,
and it will cause unreliable transcriptions.

Pay close attention to the EOU settings and the Pause threshold, adjust this as needed, lower pause and higher threshold will give you quicker response, (hopefully)
lowering the EOU threshold will gurantee faster response, but at the cost of more interruptions.
EOU Detection is not an exact science, but live-kit's model does a really good job at detecting and giving a simulated feel for a real conversation,
if the settings are set right and it's fed the right data.  IF you are using a chatbot, or virtual assistant where the next conversation relies on the past context,
you should feed that chat back to live-transcribe in the custom_callback through a return statement. (Instructions Below)

EOU_THRESHOLD = 0.74
MAX_PAUSE_THRESHOLD = .7

You have a fallback timer if a translation get's stuck and doesnt pass the EOU threshold, but a long pause is made, obviously implying the EOU

MAX_SILENCE_TIMEOUT = 3 #3s fallback timer

This is how simple VAD's work, they pay attention to the time from last word and when there's enough silence it passes it through, which works. 
But it makes for longer response times that makes the flow of the conversation not realistic.  But it's good to fallback on this, bc the EOU is not 
100% and you don't want stuck translations.  Making this timer longer will gurantee that you don't cut someone short, but at the cost of having longer
responses.  (Remember your probably sending this transcript to a llm to get some sort of response, so every second counts.)

Live-transcribe is default set to run in english mode, this makes for faster transcriptions/less resources.  If you need it to run on different languages
then you will need to change this line of code.

segments, info = whisper_model.transcribe(audio_data, language="en")

I have no idea how reliable this is, or if it even works as I only speak english.  But I thought you should know it exists.  


**Real-time speech transcription using Whisper AI, optimized for Python.**  
Supports **1-channel and 2-channel live transcription**, **AI-powered sentence correction**, and **GPU acceleration (CUDA).**  

This is a **live-transcribe module** I originally built for my **Interview Helper Assistant**, but it can be used for many other applications:  
🔹 **Live AI interviewers**  
🔹 **Chat programs**  
🔹 **Phone call transcriptions**  
🔹 **Real-time speech analysis**  

It **handles two audio streams simultaneously** (e.g., **Microphone & System Audio**) without interruptions and includes:  
🔸 **Voice Activity Detection (VAD)** – Detects speaking, silence, and pauses  
🔸 **Smart noise filtering** – Removes unwanted noise and filler words  
🔸 **AI-powered correction** – Uses **Mistral** to fix transcription errors (customizable with whitelist words)  
🔸 **Low-latency performance** – Runs efficiently on CPU/GPU with CUDA support  
🔸 **End-of-Utterance Detection (EOU)** – Powered by **LiveKit's Turn Detector Model**, transcribes when the user finishes speaking  
🔸 **📞 Live Twilio Audio Streaming** – Real-time transcription from phone calls or SIP audio

---

## 📦 **Installation**
### **1️⃣ Install Live-Transcribe**
```bash
pip install --upgrade git+https://github.com/Wesman687/live-transcribe.git
```

### **2️⃣ (Optional) Install CUDA-Optimized Version**
If you have a **GPU** and want to enable CUDA support:
```bash
pip install torch torchaudio -f https://download.pytorch.org/whl/cu118.html
```

---

## ⚡ **Quick Start**
### **1️⃣ Run the Example**
```bash
python main.py
```

### **2️⃣ Download Turn Detector Model**
```bash
python download_models.py
```
This downloads the **LiveKit Turn Detector ONNX model** used for end-of-utterance prediction.

---

## 🛠️ **Features**
👉 **Real-time transcription** using Whisper AI  
👉 **AI-powered sentence correction** (via `ollama`)  
👉 **Customizable background noise filtering**  
👉 **Supports GPU acceleration (CUDA)**  
👉 **Toggle recording on/off**  
👉 **Capture both microphone and/or system audio streams**  
👉 **Transcript Callback to handle transcription events**  
👉 **Speaking State Callback to detect when a speaker is talking**  
👉 **Digital Streams for Twilio, VOIP, or pre-recorded Audio. Plug and Play**  
👉 **EOU Detection using ONNX + LiveKit model**  
👉 **Live phone transcription via Twilio media streaming**

---

## 🧠 **EOU (End-of-Utterance) Detection**
We use **LiveKit's `turn-detector` ONNX model** to predict if the speaker has finished their sentence.

### 🔍 Why EOU Matters
Without proper sentence-ending detection, your AI may:
- Cut off the user mid-sentence
- Respond too slowly
- Misinterpret timing and intent

### ⚙️ New EOU Variables in `config.py`
```python
MIN_EOU_INTERVAL = 0.6  # Minimum time between EOU checks
MAX_EOU_RETRIES = 7  # How many retries before we force transcription
EOU_THRESHOLD = 0.74  # Confidence threshold for ending utterance
```

### 🧪 Tweak for Speed vs Accuracy
- Lower `EOU_THRESHOLD` = faster, less accurate
- Higher `EOU_THRESHOLD` = slower, more precise

EOU is checked **concurrently with Whisper**, but Whisper transcribes first. If silence goes beyond timeout (`MAX_SILENCE_TIMEOUT`), transcription is forced.

### 🧠 Credits
This feature is powered by [LiveKit's open-source turn-detector model](https://github.com/livekit/turn-detector).

---

## 🛠️ **Configuration (`config.py`)**
You can **customize settings** by modifying `config.py`.

### **📉 Whisper Model Options**
```python
MODEL_SIZE = "large-v3"
```

### **📉 Device & Precision Settings**
```python
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
```

### **📉 Junk Response Filtering**
```python
JUNK_RESPONSES = {"uh", "uhh", "uh huh", "hmm", "hmmm", "okay", "ok", "right", "yeah", "yep", "yup"}
```

### **📉 AI-Powered Transcription Fixes**
```python
FIX_TRANSCRIPTION = True
WHITELIST_WORDS = [
    "TypeScript", "JavaScript", "Python", "Redux", "React", "Next.js",
    "Node.js", "Django", "Flask", "PostgreSQL", "MongoDB",
    "company", "career", "framework", "full-stack", "developer"
]
EXAMPLE_FIXES = [
    ("I use Redux to handle date management", "I use Redux to handle state management."),
    ("The time complexity is one o'clock", "The time complexity is O(n)."),
    ("Great bit for your honey", "Great fit for your company."),
    ("I use TypeScript", "I use Django"),  # ❌ INCORRECT
    ("Your company", "Your career path")   # ❌ INCORRECT
]
```


### **📉 Misc Settings**
```python
CHANNELS = 1
RECORDING = False
MAX_MEANINGFUL_WORDS = 2
MIN_MEANINGFUL_WORD = 1
MEANINGFUL_ON = True

MAX_PAUSE_THRESHOLD = .7 # This is the pause to start the transcribe so we can check the EOU for a quicker response
MAX_SILENCE_TIMEOUT = 3 # This will bex max silence time we will wait even if there is no EOU detected
MAX_DIGITAL_VOLUME_THRESHOLD = .05  #Volume to detect speech
SPEECH_THRESHOLD = 1800  # 🔥 Increase to ignore background noise
MIN_VOLUME_THRESHOLD = 1800  # 🔥 Ignore very quiet sounds
NOISE_DURATION_THRESHOLD = 1  # 🔥 Speech must last 0.7s to be detected
IGNORE_FIRST_SECONDS = 1.5  # 🔥 Ignore small noises right after unpausing
PAUSE_THRESHOLD = 1  # 🔥 If no speech detected for 3s, consider it a break used in audio

```

---

## 🌟 **Using `live-transcribe` in Custom Applications**
### **🔹 Toggle Recording**
```python
from lt_app.audio import toggle_recording
toggle_recording()  # Start or stop recording
```

### **🔹 Handling Audio Streams**
```python
import sounddevice as sd
from lt_app.audio import mic_callback, system_callback, digital_callback

mic_stream = sd.InputStream(samplerate=16000, channels=1, callback=mic_callback, dtype="int16", device=1)
system_stream = sd.InputStream(samplerate=16000, channels=1, callback=system_callback, dtype="int16", device=3)

digital_stream(audio_data, callback)  # Plug and play for VOIP/Twilio

mic_stream.start()
system_stream.start()
digital_stream.start()
```

### **🔹 Callback Example for Transcriptions**
```python
async def custom_callback(transcript, source):
    print(f"{source}: {transcript}")
    #For chat bots you can return their response to add it to the conversation, this will make the EOU more accurate.
    #The full chat feed is fed into the EOU Model, to help determine if you've completed your thought.
    response = LLM.send_chat_to_tammy(transcript)
    return {"role": "Tammy", "content": response}


```

### **🔹 Callback Example for Speaking State Detection**
```python
def speaking_state_callback(source, is_speaking):
    state = "Speaking" if is_speaking else "Silent"
    print(f"🔔 {source.capitalize()} is now {state}")

```

---

## 🛠️ **Development & Contributions**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Wesman687/live-transcribe.git
cd live-transcribe
```

---

## 📱 **Need Help?**
- **GitHub Issues**: [https://github.com/Wesman687/live-transcribe/issues](https://github.com/Wesman687/live-transcribe/issues)  
- **Contact**: wesman687@gmail.com  

🚀 **Enjoy real-time transcription with `live-transcribe`!** 🚀
