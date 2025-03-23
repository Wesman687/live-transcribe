### **🎤 Live Transcribe**  
**Real-time speech transcription using Whisper AI, optimized for Python.**  
Supports **1-channel and 2-channel live transcription**, **AI-powered sentence correction**, and **GPU acceleration (CUDA).**  

This is a **live-transcribe module** I originally built for my **Interview Helper Assistant**, but it can be used for many other applications:  
🔹 **Live AI interviewers**  
🔹 **Chat programs**  
🔹 **Phone call transcriptions**  
🔹 **Real-time speech analysis**  
🔹 **Now handles live Twilio Stream**

It **handles two audio streams simultaneously** (e.g., **Microphone & System Audio**) without interruptions and includes:  
🔸 **Voice Activity Detection (VAD)** – Detects speaking, silence, and pauses  
🔸 **Smart noise filtering** – Removes unwanted noise and filler words  
🔸 **AI-powered correction** – Uses **Mistral** to fix transcription errors (customizable with whitelist words)  
🔸 **Low-latency performance** – Runs efficiently on CPU/GPU with CUDA support  
🔸 **End-of-Utterance Detection (EOU)** – Powered by **LiveKit's Turn Detector Model**, transcribes when the user finishes speaking

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
### **3️⃣ Download Turn Detector Model (EOU)**
This is required to use the end-of-utterance feature:
```bash
from huggingface_hub import snapshot_download
snapshot_download(repo_id="livekit/turn-detector", revision="v1.2.1", local_dir="models/turn-detector")
```
This will download the model files including `model.onnx` and tokenizer configs into your project folder.

---
---

## ⚡ **Quick Start**
### **1️⃣ Run the Example**
```bash
python main.py
```

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
I upgraded to v3-turbo and setup the en-flag it's now a lot more accurate.
MODEL_SIZE = "large-v3-turbo"
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


Just pass in the audio_stream from the websocket and your good to go, This took me a while to get right.  There's not a lot of documenation for this
digital_stream(audio_data, callback)  # Plug and play for VOIP/Twilio I'll probably rename this to twilio_stream

mic_stream.start()
system_stream.start()
digital_stream.start()
```

### **🔹 Callback Example for Transcriptions**
```python
async def custom_callback(transcript, source):
    print(f"{source}: {transcript}")
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
