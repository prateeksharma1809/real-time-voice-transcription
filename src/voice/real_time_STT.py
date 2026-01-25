import sys
import queue
import sounddevice as sd
import numpy as np
import whisper
import threading

# -----------------------------
# CONFIGURATION
# -----------------------------
MODEL_NAME = "base"  # Options: tiny, base, small, medium, large
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
BLOCK_SIZE = 1024    # Audio block size for streaming

# -----------------------------
# LOAD WHISPER MODEL
# -----------------------------
print("Loading Whisper model...")
model = whisper.load_model(MODEL_NAME)

# -----------------------------
# AUDIO QUEUE FOR STREAMING
# -----------------------------
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback from sounddevice to collect audio chunks."""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    # Convert to mono and float32
    audio_queue.put(indata.copy())

# -----------------------------
# TRANSCRIPTION THREAD
# -----------------------------
def transcribe_stream():
    """Continuously read audio from queue and transcribe."""
    buffer = np.zeros(0, dtype=np.float32)
    while True:
        try:
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data[:, 0]))  # Mono channel

            # Process in ~5 second chunks
            if len(buffer) > SAMPLE_RATE * 5:
                # Run Whisper transcription
                result = model.transcribe(buffer, fp16=False)
                print("You said:", result["text"].strip()) # type: ignore

                # Keep last 1 second of audio to avoid cutting words
                buffer = buffer[-SAMPLE_RATE:]
        except Exception as e:
            print(f"Error in transcription: {e}", file=sys.stderr)

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    try:
        # Start transcription thread
        threading.Thread(target=transcribe_stream, daemon=True).start()

        # Start audio stream
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback
        ):
            print("🎤 Listening... Press Ctrl+C to stop.")
            while True:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\nStopping transcription...")
    except Exception as e:
        print(f"Error: {e}")
