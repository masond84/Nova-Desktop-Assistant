import threading
import time
from voice import speak_response

def schedule_reminder(message, delay_seconds):
    def reminder():
        speak_response(f"Reminder: {message}")
    threading.Timer(delay_seconds, reminder).start()