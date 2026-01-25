from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)
    

if __name__ == '__main__':
    recorder = AudioToTextRecorder()
    print("Speak now...")
    while True:
        recorder.text(process_text)