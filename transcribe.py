import whisper
import os

FILENAME = "recorded.wav"

# Load the Whisper model once (outside the function for reuse)
# You can use: "base", "small", "medium", or "large"
# "medium" provides great balance between speed and accuracy
model = whisper.load_model("medium")

def transcribe_audio():
    print("Transcribing audio...")

    # Resolve absolute path to file
    filepath = os.path.abspath(FILENAME)

    # Run Whisper transcription
    result = model.transcribe(filepath)

    # Extract the transcription result
    transcript = result.get("text", "").strip()

    if transcript:
        print(f"You said: {transcript}")
        return transcript
    else:
        print("Could not understand anything.")
        return "Sorry, I couldn't catch that"