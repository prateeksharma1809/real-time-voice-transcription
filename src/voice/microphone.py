import time
import audioop
import speech_recognition as sr


SILENCE_THRESHOLD = 1500     # adjust based on your microphone sensitivity
SILENCE_DURATION = 3          # seconds of silence before stopping

def listen_until_silence():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio_data = b""
        last_sound_time = time.time()

        # use the streaming mode
        for chunk in recognizer.listen(source, stream=True): #type: ignore
            audio_chunk = chunk.get_raw_data()
            audio_data += audio_chunk

            # detect loudness
            rms = audioop.rms(audio_chunk, 2)  # root-mean-square loudness
            if rms > SILENCE_THRESHOLD:
                print("Sound detected...")
                last_sound_time = time.time()

            # stop after SILENCE_DURATION of no sound
            if time.time() - last_sound_time > SILENCE_DURATION:
                print("Silence detected, stopping...")
                break

    return sr.AudioData(audio_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)