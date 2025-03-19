import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "app")

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


import signal
import numpy as np
from pynput import keyboard
import sounddevice as sd
import asyncio
import threading

from lt_app.audio import mic_callback, system_callback, toggle_recording
from lt_app.config import CHANNELS, SAMPLE_RATE
from lt_app.transcriber import transcribe_audio
import lt_app.config as config

CUSTOM_SPEAKER_LABEL = "Caller" 
full_transcription = []
async def store_transcription_callback(transcript, source, custom_label="Recruiter"):
    """Store transcription in memory and write to file in real-time with a customizable speaker label."""
    global full_transcription
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
    speaker = "Me" if source == "mic" else custom_label  # 🔥 Use the custom label

    formatted_text = f"[{timestamp}] {speaker}: {transcript}"
    print(f"{speaker}: {transcript}")
    # ✅ Append to full_transcription list
    full_transcription.append(formatted_text)

    # ✅ Write to file immediately
    with open("transcript.txt", "a", encoding="utf-8") as f:
        f.write(formatted_text + "\n")

    # ✅ Optionally print or log it
    
async def custom_callback(transcript, source):
    """Pass the custom label to the main callback."""
    await store_transcription_callback(transcript, source, custom_label=CUSTOM_SPEAKER_LABEL)

def speaking_state_callback(source, is_speaking):
    """Handle the speaking state changes."""
    state = "Speaking" if is_speaking else "Silent"
    print(f"🔔 {source.capitalize()} is now {state}")


def on_press(key):
    """Toggle recording when spacebar is pressed."""

    if key == keyboard.Key.esc:
        cleanup()
        exit(0)

    if key == keyboard.Key.space:
        toggle_recording()

mic_stream = None
system_stream = None
listener = None

def cleanup():
    """ Clean up resources when exiting and print the full transcript. """
    global listener, mic_stream, system_stream

    print("\n🛑 Exiting... Cleaning up resources.")

    # ✅ Stop streams safely
    try:
        if mic_stream and mic_stream.active:
            mic_stream.close()
        if system_stream and system_stream.active:
            system_stream.close()
        if listener and listener.running:
            listener.stop()
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    print("✅ Cleanup complete. Goodbye!")

# ✅ Handle Ctrl+C (KeyboardInterrupt)
def signal_handler(sig, frame):
    cleanup()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)  # Register Ctrl+C handler



def run_keyboard_listener():
    """Run the keyboard listener in a separate thread so it doesn't block asyncio."""
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

async def main():
    """Main loop to handle keyboard input and audio processing."""
    global mic_stream, system_stream

    try:

        # 🔹 Try opening the microphone stream
        try:
            mic_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                callback=lambda *args: mic_callback(*args, speaking_callback=speaking_state_callback),
                dtype=np.int16,
                device=1
            )
            mic_stream.start()
            print("🎙️ Microphone stream started.")
        except Exception as mic_error:
            print(f"❌ Mic Audio device error: {mic_error}")
            mic_stream = None  # Set to None so we can still run without it

        # 🔹 Try opening the system audio (loopback) stream
        try:
            system_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                callback=lambda *args: system_callback(*args, speaking_callback=speaking_state_callback),
                dtype=np.int16,
                device=3
            )
            system_stream.start()
            print("🔊 System audio stream started.")
        except Exception as system_error:
            print(f"❌ System Audio device error: {system_error}")
            system_stream = None  # Set to None so we can still run without it

        # If both failed, exit gracefully
        if not mic_stream or not system_stream:
            print("❌ Both audio devices failed. Exiting...")
            cleanup()
            exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        cleanup()
        exit(1)

    print("🎤 Press [SPACE] to start/pause transcription. ")
    
    try:
        # 🔥 Ensure transcribe_audio is actually started
        print("🚀 Starting transcription loop...")
        loop = asyncio.get_event_loop()
        loop.create_task(transcribe_audio(custom_callback))
        print("✅ Transcription task should now be running!")

        keyboard_thread = threading.Thread(target=run_keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"❌ Error starting transcribe_audio: {e}")
        
# ✅ Run main function
asyncio.run(main())
