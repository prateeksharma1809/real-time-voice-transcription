from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import whisper
import tempfile
import os
import asyncio
from pathlib import Path
import numpy as np
import io
import wave

app = FastAPI(title="Voice Transcription API")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model (using 'base' for balance of speed/accuracy)
# Options: tiny, base, small, medium, large
model = whisper.load_model("base")

@app.get("/")
async def root():
    return {"message": "Voice Transcription API", "status": "running"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an audio file
    Accepts: wav, mp3, m4a, flac, ogg, etc.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Transcribe
        result = model.transcribe(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for streaming audio transcription
    Client sends audio chunks, server streams back transcription results
    """
    await websocket.accept()
    
    audio_buffer = bytearray()
    chunk_duration = 3  # Process every 3 seconds of audio
    sample_rate = 16000  # Whisper expects 16kHz
    bytes_per_chunk = sample_rate * chunk_duration * 2  # 16-bit audio = 2 bytes per sample
    
    try:
        while True:
            # Receive audio chunk from client
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # Process when we have enough audio
            if len(audio_buffer) >= bytes_per_chunk:
                # Extract chunk to process
                chunk_data = bytes(audio_buffer[:bytes_per_chunk])
                audio_buffer = audio_buffer[bytes_per_chunk:]
                
                # Save chunk temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    # Create WAV file
                    with wave.open(tmp.name, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(chunk_data)
                    
                    tmp_path = tmp.name
                
                try:
                    # Transcribe chunk
                    result = model.transcribe(tmp_path, language="en")
                    
                    # Send result back to client
                    await websocket.send_json({
                        "success": True,
                        "text": result["text"],
                        "is_final": False
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "success": False,
                        "error": str(e)
                    })
                
                finally:
                    # Clean up temp file
                    os.unlink(tmp_path)
    
    except WebSocketDisconnect:
        print("Client disconnected")
        
        # Process remaining audio in buffer if any
        if len(audio_buffer) > 0:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    with wave.open(tmp.name, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(bytes(audio_buffer))
                    
                    result = model.transcribe(tmp.name, language="en")
                    print(f"Final transcription: {result['text']}")
                    os.unlink(tmp.name)
            except Exception as e:
                print(f"Error processing final buffer: {e}")

@app.get("/models")
async def list_models():
    """List available Whisper models"""
    return {
        "available_models": ["tiny", "base", "small", "medium", "large"],
        "current_model": "base",
        "note": "Change model by modifying the load_model() call in code"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)