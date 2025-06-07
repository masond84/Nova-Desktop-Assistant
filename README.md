# Nova Voice Assistant
A smart, local-first voice assistant that listens for the wake word "Hey Nova," transcribes voice input using OpenAI Whisper, responds with dynamic memory-driven conversations via GPT, and stores facts in Supabase and local storage.

---
####  Features
- Wake-word detection with **Porcupine**
- Long-term memory saved in **Supabase** and `user_memory.json`
- Responses powered by **OpenAI GPT**
- Voice transcription using **Whisper**
- Text-to-speech response via **pyttsx3**
- Offline fallback with JSON-based memory store

---
#### Requirements
- Python 3.10 or newer
- OpenAI API key
- Supabase project + API credentials
- Porcupine `.ppn` wake-word model (included)

---
#### Setup Instructions
##### 1. Clone this repo
```bash
git clone https://github.com/yourusername/nova-voice-assistant.git
cd nova-voice-assistant
```
##### 2. Create and activate a virtual env
```bash
python -m venv agentEnv
.\agentEnv\Scripts\activate
```
##### 3. Install dependencies
```bash
pip install -r requirements.txt
```
Make sure FFmpeg is installed and added to System PATH
Add to system environment variables
```bash
Download from: https://www.gyan.dev/ffmpeg/builds/
Add the /bin folder path (e.g., C:\ffmpeg\bin) to your system environment variables.
```
##### 4. Add environment variables
Create a `.env` file and add
```bash
OPENAI_API_KEY=your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```
##### 5. Start the assistant
```bash
python assistant.py
```
If successful, you should see:
```bash
🔊 Porcupine wake word engine listening for 'Hey Nova'...
🔁 Press [Enter] to ask something or type 'exit' to quit:
```

---
#### A Testing Workflow Should Be
1. Say "Hey Nova"
2. Press [ENTER]
3. Speak to Nova
4. Nova will transcribe, respond using GPT, and speak back the reply.

