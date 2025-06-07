import pvporcupine
import pyaudio
import struct
import os
from core import process_conversation
from wakeword import triggered

# Path to .ppn file
WAKEWORD_PATH = os.path.join("wakewords", "Hey-Nova_en_windows_v3_0_0.ppn")

# Picovoice accesskey
ACCESS_KEY = "85S/OPMOhAntSmAnyJC+iBYHhM55IBU2vGVK3MmV1eKU5Azpv1kN8A=="

def wakeword_listener(trigger_callback):
    print("🔊 Porcupine wake word engine listening for 'Hey Nova'...")

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[WAKEWORD_PATH],
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print("✅ Wake word detected: 'Hey Nova'")
                process_conversation()  # Call your assistant logic

    except KeyboardInterrupt:
        print("❌ Wake word detection stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()