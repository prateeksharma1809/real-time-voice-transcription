# real time local voice transcription 🤖

It is a small voice-enabled assistant project that connects real-time speech-to-text (STT) and a language model to enable conversational interactions.

---

## Quick start ✅

1. Install dependencies:

```bash
pip install -r requirenments.txt
```

> **Note:** The repository currently contains a file named `requirenments.txt` (typo). Rename it to `requirements.txt` if you prefer the conventional name.

2. Run the app:

```bash
python main.py
```

3. Typical flow: microphone input → STT/transcription → LLM processing → (response delivered back in your app).

---

## Project structure 🔧

```
main.py
requirenments.txt
data/
src/
  config.py
  chat/
    llm.py
  voice/
    microphone.py
    real_time_STT.py
    transcribe_audio.py
    transcriber.py
    wake_word_transcription.py
```

### Files & folders (what they do) 💡

- `main.py` — smallest way to transcribe the audio from microphone in real-time using STT

- `requirenments.txt` — Lists Python dependencies. (See note above about the filename typo.)

- `data/` — Storage for runtime data (conversation logs, cached audio, artifacts). Add project-specific files here.

- `src/config.py` — Central configuration: API keys, model settings, timeouts and other environment-specific settings. Keep secrets out of the repo.

- `src/chat/llm.py` — Language model interface and prompt logic. Encapsulates calls to the chosen LLM provider, handles prompt construction, response parsing, and conversation state.

- `src/voice/microphone.py` — Microphone and audio capture utilities. Handles low-level access to the system mic and returns audio frames or files for processing.

- `src/voice/real_time_STT.py` — Real-time streaming STT manager: streams audio to an STT service and yields partial/final transcripts as they arrive.

- `src/voice/transcribe_audio.py` — Batch transcription utilities for processing recorded audio files (non-realtime jobs).

- `src/voice/transcriber.py` — Core transcription logic: wrappers around STT backends, model selection, segmentation, retry and error handling.

- `src/voice/wake_word_transcription.py` — Wake word detection and short phrase transcription; used to trigger the assistant from passive listening mode.

---

