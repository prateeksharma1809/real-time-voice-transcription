import speech_recognition as sr
import tempfile
import os
# Try to import whisper (local transcription). If not available, we'll use Google API.
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

class Transcriber:
    def __init__(self, use_whisper=WHISPER_AVAILABLE, whisper_model_name="base"):
        self.use_whisper = use_whisper and WHISPER_AVAILABLE
        self.whisper_model_name = whisper_model_name
        self.whisper_model = None
        if self.use_whisper:
            print(f"[Transcriber] Loading Whisper model '{self.whisper_model_name}' (this may take a while)...")
            self.whisper_model = whisper.load_model(self.whisper_model_name) # type: ignore
            print("[Transcriber] Whisper model loaded.")

    def transcribe_audiodata(self, audio_data: sr.AudioData) -> str:
        """
        Given speech_recognition.AudioData, return a transcription string.
        Uses whisper (local) if available, otherwise falls back to Google Web Speech API.
        """
        if self.use_whisper and self.whisper_model is not None:
            # Write to temporary WAV and call whisper.transcribe
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpf:
                tmp_path = tmpf.name
                tmpf.write(audio_data.get_wav_data())
            try:
                result = self.whisper_model.transcribe(tmp_path)
                text = result.get("text", "").strip() # type: ignore
                return text
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        else:
            # Fallback: Google Web Speech (requires internet)
            recognizer = sr.Recognizer()
            try:
                return recognizer.recognize_google(audio_data) # type: ignore
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                return f"[ERROR: {e}]"
