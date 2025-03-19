
This is a live-transcribe I made for an Interview Helper Assistant I am making.  It can be used for a multitude of projects though,
it handles one or two channels that differentiates speakers.  Such as Mic or System Audio.
It has VAD detection, that detects speaking, silence, pauses, also uses smart filtering tech to filter out junk noices.
Junk Filtering can be turned off. 
Also uses Mistral to fix incorrect transcriptions, that can be fine tuned with white list words.  
It handles both channels simultaneously, so one person speaking doesn't interrupt the other. 

This is basically a starting point for live AI Interviewers, Chat Programs, Phone Calls, etc.

Let me know if you have any improvements, it would be gladly helpful.  This is just a private project i'm working on and
thought others could find it Useful 


## 🎤 Live Transcribe
**Real-time speech transcription using Whisper AI, optimized for Python.**  
Supports **1 channel and 2 channel live transcription**, **AI processing**, and **GPU acceleration (CUDA).**


---

## 📦 Installation
### **1️⃣ Install 
pip install --upgrade git+https://github.com/Wesman687/live-transcribe.git

### **2️⃣ (Optional) Install CUDA-Optimized Version**
If you have a **GPU** and want to enable CUDA support:
```bash
pip install torchaudio -f https://download.pytorch.org/whl/cu118.html
```

---

## ⚡ Quick Start
### **1️⃣ Run the Example**
```bash
python main.py
```


## 🛠️ Features
✅ **Real-time transcription** using Whisper AI  
✅ **AI-powered sentence correction** (via `ollama`)  
✅ **Customizable background noise filtering**  
✅ **Supports GPU acceleration (CUDA)**    
✅ **Toggle recording on/off**  
✅ **Capture both microphone and/or system audio streams**  
✅ **Transcript Callback to do further functions with transcription**
✅ **Speaking Callback for identifying when a channel is speaking**

---

## 💩 Configuration
You can **customize settings** by modifying `config.py` 

SAMPLE_RATE: 16000
MAX_PAUSE_THRESHOLD: 2
SPEECH_THRESHOLD: 1400

Whisper Modals
# 🔽 SELECT THE BEST MODEL FOR YOUR COMPUTER 🔽
# --------------------------------------------
# - "tiny"    → Fastest, least accurate, ~1GB RAM
# - "base"    → Fast, lower accuracy, ~2GB RAM
# - "small"   → Balanced, moderate speed, ~4GB RAM
# - "medium"  → Slower, better accuracy, ~7GB RAM
# - "large-v3" (default) → Slowest, best accuracy, needs 10GB+ VRAM
MODEL_SIZE = "large-v3"  # Change this based on your system capabilities

# 🔽 DEVICE SELECTION (GPU vs CPU) 🔽
# -----------------------------------
# - "cuda" → Use GPU (best for NVIDIA GPUs with CUDA support)
# - "cpu"  → Use CPU only (for slower PCs or non-GPU devices)
DEVICE = "cuda"  # Change to "cpu" if you don't have a GPU

# 🔽 COMPUTE TYPE (Precision Optimization) 🔽
# -------------------------------------------
# - "float16" → Uses Half Precision (Recommended for GPUs, saves VRAM)
# - "float32" → Full Precision (More accurate, but uses more VRAM)
# - "int8"    → Lowest Precision (Best for CPUs, lowest RAM usage)
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"


Junk Responses filters out unnecessary words, short phrases you don't want in your transcriptions.
Some reason the Whisper likes to add in "thanks for watching", the filters automatically filters this out.

FIX Transcriptions, helps fix mispellings and halluecinations. 
WHITELIST_WORDS helps train the mistral modal to identify popular words you may say.


FIX_TRANSCRIPTION = True
JUNK_RESPONSES = {"uh", "uhh", "uh huh", "hmm", "hmmm", "okay", "ok", "right", "yeah", "yep", "yup"}

WHITELIST_WORDS = [
    "TypeScript", "JavaScript", "Python", "Redux", "React", "Next.js",
    "Node.js", "Django", "Flask", "PostgreSQL", "MongoDB",
    "company", "career", "framework", "full-stack", "developer", "full-stack", "Paul Miracle"]
---

## 🛠️ Setting Up Virtual Audio Cable (For System Audio Transcription)
To capture **both microphone and system audio**, you may need **Virtual Audio Cable** (VAC).  
This allows the program to listen to desktop/system sounds as an additional input.

### **1️⃣ Download & Install Virtual Audio Cable**
- **Windows:** Download from [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)  
- **macOS:** Use **Loopback** (paid) or **BlackHole** (free) → [https://existential.audio/blackhole/](https://existential.audio/blackhole/)
- **Linux:** Use **PulseAudio** with `pactl` or **JACK Audio**

### **2️⃣ Set Up the Virtual Audio Device**
#### **Windows Setup (VB-Audio Cable)**

1. Open **Sound Settings** → Go to **Recording Devices**
2. Find `CABLE Output (VB-Audio Virtual Cable)` and **Set as Default Device**
3. In **Playback Devices**, select `CABLE Input (VB-Audio Virtual Cable)` as the output for system audio.
4. Restart any apps using audio and test with:
   ```bash
   python examples/main.py
   ```

#### **macOS Setup (BlackHole)**
1. Install BlackHole and open **Audio MIDI Setup**
2. Create a new **Multi-Output Device**
3. Set BlackHole as one of the outputs and use it in your program.

#### **Linux Setup (PulseAudio)**
```bash
pactl load-module module-null-sink sink_name=VirtualCable
pactl set-default-sink VirtualCable
```

---

## 🖥️ Running Without `main.py`
If you don't want to use the built-in `main.py`, you can create a **custom implementation**.



---

## 🔊 Handling Audio Streams & Recording Control
### **1️⃣ Toggle Recording (Start/Stop)**
By default, the program starts in a **paused** state. You can start/stop recording by pressing **spacebar**:
```python
from lt_app.audio import toggle_recording

toggle_recording()  # Start or stop recording
```

### **2️⃣ Managing Audio Streams**
The transcription system captures both **microphone** and **system (loopback) audio**:
```python
import sounddevice as sd
from lt_app.audio import mic_callback, system_callback

mic_stream = sd.InputStream(
    samplerate=16000, channels=1, callback=lambda *args: mic_callback(*args, speaking_callback=speaking_state_callback), dtype="int16", device=1
)
system_stream = sd.InputStream(
    samplerate=16000, channels=1, callback=lambda *args: mic_callback(*args, speaking_callback=speaking_state_callback),, dtype="int16", device=3
)


mic_stream.start()
system_stream.start()
```

If you need to stop the audio streams safely:
```python
mic_stream.close()
system_stream.close()
```

CallBack Examples
```
async def custom_callback(transcript, source):
    """Pass the custom label to the main callback."""
    await store_transcription_callback(transcript, source, custom_label=CUSTOM_SPEAKER_LABEL)
    print(f"{source}: {transcript})

def speaking_state_callback(source, is_speaking):
    """Handle the speaking state changes."""
    state = "Speaking" if is_speaking else "Silent"
    print(f"🔔 {source.capitalize()} is now {state}")
```

---

## ⚙️ Advanced Setup
### **Check if CUDA is Enabled**
Run the following inside Python:
```python
import torch
print("CUDA Available:", torch.cuda.is_available())
```

If `False`, install CUDA-optimized `torchaudio`:
```bash
pip install torchaudio -f https://download.pytorch.org/whl/cu118.html
```

---

## 🛠️ Development & Contributions
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Wesman687/live-transcribe.git
cd live-transcribe
```

---

## 📞 Need Help?
- **GitHub Issues**: [https://github.com/yourgithub/live-transcribe/issues](https://github.com/Wesman687/live-transcribe/issues)  
- **Contact**: wesman687@gmail.com  

🚀 **Enjoy real-time transcription with `live-transcribe`!** 🚀