import asyncio
from whisper_live.client import TranscriptionClient


# Neeed yo run "whisper-live --model base" before running this 
# -----------------------------
# CONFIGURATION
# -----------------------------
WAKE_WORD = "computer"  # Change to your desired wake word
SERVER_URL = "localhost"
SERVER_PORT = 9090
MODEL_NAME = "base"  # tiny, base, small, medium, large

# -----------------------------
# WAKE WORD HANDLER
# -----------------------------
def handle_transcription(text: str):
    """Process transcribed text and check for wake word."""
    print(f"Partial: {text}")
    if WAKE_WORD.lower() in text.lower():
        print("Wake word detected! Listening for command...")

# -----------------------------
# MAIN ASYNC FUNCTION
# -----------------------------
async def main():
    # Connect to whisper-live server
    client = TranscriptionClient(SERVER_URL, SERVER_PORT)
    await client.connect() # type: ignore

    # Start microphone streaming
    await client.stream_microphone( # type: ignore
        model=MODEL_NAME,
        translate=False,
        on_transcription=handle_transcription
    )

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
