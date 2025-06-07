import os
import webbrowser
import re
from reminders import schedule_reminder
from timers import start_timer

number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

def open_search_query(query: str, site_hint=None):
    """Performs a web search or site open based on user query"""
    base = "https://www.google.com/search?q="
    if site_hint:
        query = f"{site_hint} site:{site_hint}"
    search_url = base + query.replace(" ", "+")
    webbrowser.open(search_url)
    return f"Searching for: {query}"

def execute_command(prompt: str):
    prompt = prompt.lower().strip()
    
    # Open file explorer to Downloads
    if "open downloads" in prompt:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.startfile(downloads_path)
        return "Opening Downloads Folder."
    # Launch Google Chrome
    elif "open chrome" in prompt:
        os.system("start chrome")
        return "Launching Google Chrome."
    # Reminders: "remind me to take a break in 20 minutes" - needs work
    elif "remind me" in prompt:
        match = re.search(r"remind me to (.+) in (\d+) (seconds|minutes|hours)", prompt)
        if match:
            task = match.group(1)
            amount = int(match.group(2))
            unit = match.group(3)

            multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}
            delay = amount * multiplier.get(unit, 60)
            schedule_reminder(task, delay)
            return f"Okay, I'll remind you to {task} in {amount} {unit}."
        return "Sorry, I couldn't understand the reminder format."
    # Timer: "Set a timer in 10 minutes" - needs work
    elif "set a timer" in prompt:
        match = re.search(r"set a timer for (\d+) (seconds|minutes|hours)", prompt)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            multiplier = {"seconds": 1, "minutes": 60, "hours": 3600}
            duration = amount * multiplier.get(unit, 60)
            start_timer(duration)
            return f"Starting a timer for {amount} {unit}."
        return "I couldn't understand the timer request."
    # Smart search or site opening: "Open GitHub", "Search Python async", etc.
    elif re.match(r"(open|search|look up|can you research|can you open)\s", prompt):
        match = re.search(r"(open|search|look up|can you research|can you open)\s(.+)", prompt)
        if match:
            raw_query = match.group(2)
            return open_search_query(raw_query)
    return None