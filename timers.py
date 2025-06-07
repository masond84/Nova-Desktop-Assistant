import threading
from voice import speak_response

def start_timer(duration_seconds):
    def notify():
        speak_response("Time's up!")
    speak_response(f"Timer started for {duration_seconds // 60} minutes.")
    threading.Timer(duration_seconds, notify).start()
