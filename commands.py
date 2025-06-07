import os
import webbrowser

def execute_command(prompt: str):
    prompt = prompt.lower().strip()

    if "open youtube" in prompt:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "open google" in prompt: 
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif "open downloads" in prompt:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.startfile(downloads_path)
        return "Opening Downloads Folder."
    elif "open chrome" in prompt:
        os.system("start chrome")
        return "Launching Google Chrome."

    return None