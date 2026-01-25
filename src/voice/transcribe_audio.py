import speech_recognition as sr
import os
import threading
import queue
from datetime import datetime
from transcriber import Transcriber

r = sr.Recognizer()

t = Transcriber()
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

SENTINEL = object()

def transcribe_audio(filename=None):
    """Start a non-blocking producer/consumer pipeline for transcription.

    Producer thread: captures audio and pushes AudioData objects into audio_queue.
    Recognizer thread: consumes AudioData, transcribes, pushes text into text_queue.
    Saver thread: consumes text and writes to disk (and prints).
    """

    audio_queue: queue.Queue[sr.AudioData | object] = queue.Queue()
    text_queue: queue.Queue[str | object] = queue.Queue()

    def producer():
        with sr.Microphone() as source:
            print("warming up...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Please speak now... (Ctrl+C to stop)")
            while True:
                try:
                    audio_data = r.listen(source, timeout=5, phrase_time_limit=10)
                    audio_queue.put(audio_data)
                except sr.WaitTimeoutError:
                    print("No speech detected, stopping producer.")
                    break
                except Exception as e:
                    print(f"Producer error: {e}; stopping producer.")
                    break
        # signal recognizer to finish
        audio_queue.put(SENTINEL)

    def recognizer():
        while True:
            item = audio_queue.get()
            if item is SENTINEL:
                # pass sentinel downstream
                text_queue.put(SENTINEL)
                break
            try:
                text = recognize_speech(item)
                if text:
                    text_queue.put(text)
            except Exception as e:
                text_queue.put(f"[Recognizer error: {e}]")
        audio_queue.task_done()

    def saver():
        while True:
            item = text_queue.get()
            if item is SENTINEL:
                break
            save_transcription(item, filename)
            text_queue.task_done()

    producer_thread = threading.Thread(target=producer, daemon=True)
    recognizer_thread = threading.Thread(target=recognizer, daemon=True)
    saver_thread = threading.Thread(target=saver, daemon=True)

    producer_thread.start()
    recognizer_thread.start()
    saver_thread.start()

    try:
        # Keep main thread alive until producer finishes, then wait for downstream
        producer_thread.join()
        recognizer_thread.join()
        saver_thread.join()
    except KeyboardInterrupt:
        print("Interrupted by user. Attempting graceful shutdown...")
        # Put sentinels if not already to unblock threads
        audio_queue.put(SENTINEL)
        text_queue.put(SENTINEL)
        recognizer_thread.join(timeout=2)
        saver_thread.join(timeout=2)
    print("Transcription pipeline finished.")


def recognize_speech(audio_data):
    try:
        text = t.transcribe_audiodata(audio_data)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {text}"
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[Could not request results; {e}]"
    except Exception as e:
        return f"[Error recognizing speech: {e}]"

# Backwards compatibility alias (if other modules still call old name)
def recognize_speach(audio_data):  # type: ignore
    return recognize_speech(audio_data)

def save_transcription(text, filename=None):
    if filename is not None:
        print(f"Saving transcription to {filename}")
        with open(filename, "a") as f:
            f.write(text + "\n")
    print(f"Transcribed: {text}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/transcription_{timestamp}.txt"
    
    if not os.path.exists(filename):
        open(filename, 'w').close()
    transcribe_audio()
    # transcribe_audio(filename)