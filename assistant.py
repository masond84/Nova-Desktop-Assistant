from core import process_conversation
from porcupine_listener import wakeword_listener
from scheduler import proactive_message_loop, update_user_activity_timestamp
import threading

def run_agent():
    # Start the bakcground thread for wake-word detection
    wake_thread = threading.Thread(target=wakeword_listener, args=(process_conversation,))
    wake_thread.daemon = True
    wake_thread.start()

    # Start proactive behavior every 15 seconds
    proactive_message_loop(min_interval=15, max_interval=60, idle_threshold=20)

    while True:
        ready = input("\n🔁 Press [Enter] to ask something or type 'exit' to quit: ")
        if ready.lower() == "exit":
            break
        update_user_activity_timestamp()
        process_conversation()

if __name__ == "__main__":
    run_agent()