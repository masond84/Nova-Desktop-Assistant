import speech_recognition as sr
import threading

triggered = False

def wakeword_listener(trigger_callback):
    global triggered
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Wakeword detection active... Say 'Hey Nova'")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        if triggered:
            continue
        
        try:
            with mic as source:
                audio = recognizer.listen(source, phrase_time_limit=5)
            
            text = recognizer.recognize_google(audio).lower()
            print(f"Detected speech: {text}")

            if "hey nova" in text:
                print("Wakeword detected: Hey Nova")
                triggered = True
                trigger_callback()
        
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Wakeword error: {e}")