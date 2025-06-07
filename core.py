from voice import record_audio, speak_response
from transcribe import transcribe_audio
from llm import get_gpt_response
from wakeword import triggered

def process_conversation():
    global triggered
    record_audio()
    prompt = transcribe_audio()

    if not prompt.strip():
        print("Nothing detected. Try again.")
        triggered = False
        return

    response = get_gpt_response(prompt)
    speak_response(response)
    triggered = False