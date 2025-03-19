### **🎤 Live Transcribe**  
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

---

## 🛠️ **Configuration (`config.py`)**
You can **customize settings** by modifying `config.py`.

### **📉 Whisper Model Options**
```python
MODEL_SIZE = "large-v3"  # Change based on your system
```

### **📉 Device & Precision Settings**
```python
DEVICE = "cuda"  # Change to "cpu" if no GPU
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"
```

### **📉 Junk Response Filtering**
```python
JUNK_RESPONSES = {"uh", "uhh", "uh huh", "hmm", "hmmm", "okay", "ok", "right", "yeah", "yep", "yup"}
```

### **📉 AI-Powered Transcription Fixes**
```python
FIX_TRANSCRIPTION = True  # Enable AI-based transcription correction
WHITELIST_WORDS = [
    "TypeScript", "JavaScript", "Python", "Redux", "React", "Next.js",
    "Node.js", "Django", "Flask", "PostgreSQL", "MongoDB",
    "company", "career", "framework", "full-stack", "developer"
]
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
from lt_app.audio import mic_callback, system_callback

mic_stream = sd.InputStream(samplerate=16000, channels=1, callback=mic_callback, dtype="int16", device=1)
system_stream = sd.InputStream(samplerate=16000, channels=1, callback=system_callback, dtype="int16", device=3)

mic_stream.start()
system_stream.start()
```

### **🔹 Callback Example for Transcriptions**
```python
async def custom_callback(transcript, source):
    """Handle the transcription event."""
    print(f"{source}: {transcript}")
```

### **🔹 Callback Example for Speaking State Detection**
```python
def speaking_state_callback(source, is_speaking):
    """Handle the speaking state changes."""
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

