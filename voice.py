import sounddevice as sd
import numpy as np
import soundfile as sf
import webrtcvad
import collections
#from scipy.io.wavfile import write
import edge_tts
import asyncio
import pygame
import os
import time
import random

FILENAME = "recorded.wav"
RESPONSE_AUDIO = "response.mp3"
SAMPLE_RATE = 16000
FRAME_DURATION = 30
CHANNELS = 1
VAD_MODE = 3

# Capture microphone input
def record_audio():
    print("Speak Now...")

    vad = webrtcvad.Vad(VAD_MODE)
    frame_length = int(SAMPLE_RATE * FRAME_DURATION / 1000)
    buffer = collections.deque(maxlen=30)
    recording = []
    silence_counter = 0
    triggered = False

    def callback(indata, frames, time, status):
        nonlocal triggered, recording, silence_counter
        if status:
            print("Error:", status)
        
        frame = indata[:, 0].tobytes()
        is_speech = vad.is_speech(frame, SAMPLE_RATE)

        if not triggered:
            buffer.append(frame)
            if is_speech:
                triggered = True
                recording.extend(buffer)
                buffer.clear()
        else:
            recording.append(frame)
            if not is_speech:
                silence_counter += 1
            else:
                silence_counter = 0
        
        if triggered and silence_counter > 15:
            raise sd.CallbackStop()
    
    try:
        with sd.InputStream( 
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            blocksize=frame_length,
            callback=callback
        ):
            sd.sleep(10000)
    except sd.CallbackStop:
        pass

    audio_bytes = b''.join(recording)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
    sf.write(FILENAME, audio_np, SAMPLE_RATE)
    print("Recording complete.")

# Text-to-speech response
def speak_response(text):
    print("Speaking response...")
    
    async def generate_and_play():
        try:
            communicate = edge_tts.Communicate(text, voice="en-US-SteffanNeural")
            await communicate.save(RESPONSE_AUDIO)

            # Retry up to 5 times if the file doesnt show immediatly
            for _ in range(5):
                if os.path.exists(RESPONSE_AUDIO) and os.path.getsize(RESPONSE_AUDIO) > 100:
                    break
                time.sleep(0.2)

            if not os.path.exists(RESPONSE_AUDIO):
                print("⚠️ File not generated.")
                return

            print(f"✅ File saved: {RESPONSE_AUDIO}")
            pygame.mixer.init()
            try:
                pygame.mixer.music.load(RESPONSE_AUDIO)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except pygame.error as e:
                print(f"Pygame audio error: {e}")
            finally:
                pygame.mixer.music.unload()
                os.remove(RESPONSE_AUDIO)
        except Exception as e:
            print(f"Unexpected error in speak_response: {e}")    
    
    try:
        asyncio.run(generate_and_play())
    except RuntimeError:
        # Handles nested event loops (common with threads)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_and_play())