import threading
import time
import random
from llm import get_gpt_response, messages
from voice import speak_response

last_user_interaction_time = time.time()

# Call this externally every time the user interacts
def update_user_activity_timestamp():
    global last_user_interaction_time
    last_user_interaction_time = time.time()

def proactive_message_loop(min_interval=15, max_interval=60, idle_threshold=20):
    def loop():
        while True:
            wait_time = random.randint(min_interval, max_interval)
            time.sleep(wait_time)

            # Check how long it's been since last interaction
            time_since_last = time.time() - last_user_interaction_time
            if time_since_last < idle_threshold:
                continue # User is active; skip proactive message
            
            # If user has been inactive for interval seconds
            system_prompt = (
                "Based on recent messages and memory, say something helpful or kind "
                "to re-engage the user or offer assistance. "
                "Use context if available, such as what the user was just talking about."
            )
            response = get_gpt_response(system_prompt, role_override="system")
            print(f"\nNova (Proactive): {response}")
            speak_response(response)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()    