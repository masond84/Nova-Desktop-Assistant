from openai import OpenAI
import json
import os
from memory_store import fetch_user_memory, store_memory
from commands import execute_command
from dotenv import load_dotenv
load_dotenv()

# Insert your own OpenAI key here (you can replace this later with a .env loader)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Path to store/load user memory
memory_path = "user_memory.json"
log_path = "message_log.json"
message_limit = 6 # Number of turns to keep in short-term memory

# Default memory
default_memory = {
    "preferences": [],
    "hobbies": [],
    "locations": [],
}

# Load Memory: Try Supabase first, fallback to local
try:
    long_term_memory = fetch_user_memory()
    print("Memory loaded from Supabase.")
except Exception as e:
    print(f"Failed to load memory from Supabase: {e}")

    # Fallback to local
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            long_term_memory = json.load(f)
        print("Loaded memory from local file.")
    else:
        long_term_memory = default_memory.copy()
        print("No memory found. Using default memory.")

# Save merged memory locally
with open(memory_path, "w") as f:
    json.dump(long_term_memory, f, indent=2)

# Create base system prompt based on memory
def build_system_prompt():
    summary = []

    for category, facts in long_term_memory.items():
        if facts:
            summary.append(f"{category.capitalize()}: " + ", ".join(facts))

    # System prompt dynamically created from known facts
    if summary:
        return (
            "You are a helpful voice assistant named Nova." 
            "Here's what you know about the user:\n" + "\n".join(summary)
        )
    else:
        return (
            "You are a helpful voice assistant named Nova."
            "You are just starting to learn about the user."
        )

# Initialize message memory with the system prompt
messages = [
    {"role": "system", "content": build_system_prompt()}
]

# Helper function to classify user intent
def classify_intent(user_input: str) -> str:
    """
    Use GPT to decide if the user is asking to remember, forget, or do none.
    Returns: "remember", "forget", or "none"
    """
    prompt = [
        {
            "role": "system",
            "content": (
                "You categorize the user's message strictly as one of: "
                "'remember', 'forget', or 'none'."
                "Based off of the user's prompt and given inquiry please categorize and determine if the user wants to remember or forget something then return that intent only."
            ),
        },
        {"role": "user", "content": user_input},
    ]

    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
    )
    intent = result.choices[0].message.content.strip().lower()
    return intent if intent in {"remember", "forget"} else "none"

# Helper function to pull a fact and category from text
def extract_fact(user_input: str) -> dict:
    """
    Returns : {"fact": "...", "category": "..."} using GPT
    Categories: preferences, hobbies, locations.
    """
    extraction_prompt = [
        {
            "role": "system",
            "content": (
                "Extract a single fact and its category from the message. "
                "Respond ONLY with JSON like "
                '{"fact": "<fact>", "category": "<preferences|hobbies|locations>"}'
            ),
        },
        {"role": "user", "content": user_input},
    ]

    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=extraction_prompt,
    )
    return json.loads(result.choices[0].message.content)

def get_gpt_response(prompt, role_override=None):
    print("Thinking...")

    # Handle Proactive (system-triggered) messages first
    if role_override == "system":
        recent_context = [messages[0]] + messages[-message_limit:]
        recent_context.append({"role": "system", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=recent_context
        )

        reply = response.choices[0].message.content
        print(f"Assistant (Proactive): {reply}")
        return reply
    
    ### === REGULAR CONVERSATION FLOW === ###

    # Clean leading/trailing whitespace
    stripped_prompt = prompt.strip().lower()

    # Classify user intent
    intent = classify_intent(prompt)

    # 1. Check Known System Commands
    command_result = execute_command(stripped_prompt)
    if command_result:
        # Log the command as part of the conversation
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": command_result})

        # Save updated log
        with open(log_path, "w") as f:
            json.dump(messages, f, indent=2)

        print(f"Assistant (command): {command_result}")
        return command_result
    
    # 2. Handle Unknown Input - If failed to understand user
    if not stripped_prompt or stripped_prompt in [
        "sorry, i couldn't catch that",
        "could not understand anything.",
        "no input detected"
    ]:
        # Assistant should generate a dynamic natural fallback
        fallback_instruction = {
            "role": "user",
            "content": (
                "The user said something but it could not be transcribed properly or understood. "
                "Please respond kindly and naturally, as if you're trying to clarify or ask them to repeat."
            )
        }

        fallback_context = [messages[0], fallback_instruction]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=fallback_context
        )

        reply = response.choices[0].message.content
        print(f"Assistant: {reply}")
        messages.append({"role": "user", "content": "[UNINTELLIGIBLE]"})
        messages.append({"role": "assistant", "content": reply})
        return reply

    # 3. Handle Memory Listing
    if "what do you remember" in stripped_prompt or "list everything" in stripped_prompt:
        output = []
        for category, facts in long_term_memory.items():
            if facts:
                output.append(f"{category.capitalize()}: " + ", ".join(facts))
        return "\n".join(output) if output else "I don't remember anything yet."

    # 4. Handle Forgetting Facts
    if intent == "forget":
        fact_to_forget = prompt.strip().lower()
        removed = False

        for category in long_term_memory:
            original = long_term_memory[category]
            filtered = [f for f in original if fact_to_forget not in f.lower()]
            if len(filtered) < len(original):
                long_term_memory[category] = filtered
                removed = True
        if removed:
            with open(memory_path, "w") as f:
                json.dump(long_term_memory, f, indent=2)
            return f"Got it, I've learned to forget: '{fact_to_forget}'"
        return "I couldn't find that to forget." 

    # 5. Handle Memory Storage
    if intent == "remember":
        try:
            info = extract_fact(prompt)
            fact = info["fact"]
            category = info["category"]
        except Exception as e:
            print(f"Memory extraction error: {e}")
            return "Hmm, I couldn't figure out what to remember."

        if fact.lower() not in [f.lower() for f in long_term_memory[category]]:
            long_term_memory[category].append(fact)
            with open(memory_path, "w") as f:
                json.dump(long_term_memory, f, indent=2)
            try:
                store_memory(category, fact)
            except Exception as e:
                print(f"Failed to sync to Supabase: {e}")
            return f"Got it. I'll remember that under {category}: '{fact}'"
        else:
            return "I've already remembered that."

    # 6. Handle Regular GPT Conversation
    messages.append({"role": "user", "content": prompt})
    # Update system prompt with the current long-term memory
    messages[0]["content"] = build_system_prompt()
    # Limit message history to reduce token usage
    recent_context = [messages[0]] + messages[-message_limit:]
    
    # Query OpenAI with limited memory
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=recent_context
    )

    # Extract reply
    reply = response.choices[0].message.content
    print(f"Assistant: {reply}")
    # Append assistant reply to messages
    messages.append({"role": "assistant", "content": reply})

    # Save entire message history to a log file
    with open(log_path, "w") as f:
        json.dump(messages, f, indent=2)

    return reply