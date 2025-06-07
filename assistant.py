from core import process_conversation
from porcupine_listener import wakeword_listener
import threading

def run_agent():
    # Start the bakcground thread for wake-word detection
    wake_thread = threading.Thread(target=wakeword_listener, args=(process_conversation,))
    wake_thread.daemon = True
    wake_thread.start()

    while True:
        ready = input("\n🔁 Press [Enter] to ask something or type 'exit' to quit: ")
        if ready.lower() == "exit":
            break

        process_conversation()

if __name__ == "__main__":
    run_agent()