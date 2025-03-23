import time
import torch
# ✅ Check if CUDA is available


CUDA_AVAILABLE = torch.cuda.is_available()

if not CUDA_AVAILABLE:
    print("⚠️ CUDA is not available. Using CPU version of torchaudio.")
    print("🔹 If you want CUDA support, install the correct torchaudio:")
    print("   pip install torchaudio -f https://download.pytorch.org/whl/cu118.html")
else:
    print("✅ CUDA is available! Using GPU acceleration.")


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
DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"  # Change to "cpu" if you don't have a GPU

# 🔽 COMPUTE TYPE (Precision Optimization) 🔽
# -------------------------------------------
# - "float16" → Uses Half Precision (Recommended for GPUs, saves VRAM)
# - "float32" → Full Precision (More accurate, but uses more VRAM)
# - "int8"    → Lowest Precision (Best for CPUs, lowest RAM usage)
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"


SAMPLE_RATE = 16000

MAX_PAUSE_THRESHOLD = 2
MAX_DIGITAL_PAUSE_THRESHOLD = 1
SPEECH_THRESHOLD = 1800  # 🔥 Increase to ignore background noise
MIN_VOLUME_THRESHOLD = 1800  # 🔥 Ignore very quiet sounds
NOISE_DURATION_THRESHOLD = 1  # 🔥 Speech must last 0.7s to be detected
IGNORE_FIRST_SECONDS = 1.5  # 🔥 Ignore small noises right after unpausing


 # 🔥 Maximum pause threshold
PAUSE_THRESHOLD = 1.5  # 🔥 If no speech detected for 3s, consider it a break
JUNK_RESPONSES = {"uh", "uhh", "uh huh", "hmm", "hmmm", "okay", "ok", "right", "yeah", "yep", "yup"}
FIX_TRANSCRIPTION = True

WHITELIST_WORDS = [
        "TypeScript", "JavaScript", "Python", "Redux", "React", "Next.js",
        "Node.js", "Django", "Flask", "PostgreSQL", "MongoDB",
        "company", "career", "framework", "full-stack", "developer", "full-stack", "Paul Miracle"]

EXAMPLE_FIXES = [
    # Correct Fixes
    ("I use Redux to handle date management", "I use Redux to handle state management."),
    ("The time complexity is one o'clock", "The time complexity is O(n)."),
    ("Great bit for your honey", "Great fit for your company."),

    # Incorrect Fixes (Examples of what not to do)
    ("I use TypeScript", "I use Django"),  # ❌ INCORRECT
    ("Your company", "Your career path")   # ❌ INCORRECT
]

CHANNELS = 1
RECORDING = False  # ✅ Start in paused mode
MAX_MEANINGFUL_WORDS = 5
MIN_MEANINGFUL_WORD = 2
MEANINGFUL_ON = True
# ✅ Audio Buffers & State
mic_buffer = []
system_buffer = []
digital_buffer = []
last_mic_detected_time = time.time()
last_system_detected_time = time.time()
last_digital_detected_time = time.time()
last_mic_audio_time = time.time()
last_system_audio_time = time.time()
last_digital_audio_time = time.time()
start_time = time.time()  # Track when recording starts

mic_speaking = False
system_speaking = False
digital_speaking = False
