
import openai
import json
import sys
import pyaudio
import wave
import keyboard
import time
import googletrans
from playsound import playsound
from config import api_key
from yntkts.makePrompt import *
from yntkts.translate import *
from yntkts.TTS import *
from yntkts.subtitle import *

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

openai.api_key = api_key

conversation = []
history =  {"history": conversation}

mode = 0 
total_character = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
oniichan_name = "Surya"

def record_audio():
    CHUNK = 124
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")

def transcribe_audio(file):
    global chat_now
    try:
        audio_file= open(file, "rb")
        # Translating the audio to English
        # transcript = openai.Audio.translate("whisper-1", audio_file)
        # Transcribe the audio to detected language
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        chat_now = transcript.text
        print ("Question: " + chat_now)
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return

    result = oniichan_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()

def openai_answer():
    global total_characters, conversation

    total_characters = sum(len(d['content']) for d in conversation)

    while total_characters > 4000:
        try:
            # print(total_characters)
            # print(len(conversation))
            conversation.pop(2)
            total_characters = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        # Write the message data to the file in JSON format
        json.dump(history, f, indent=4)

    prompt = getPrompt()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=128,
        temperature=1,
        top_p=0.9
    )
    message = response['choices'][0]['message']['content']
    conversation.append({'role': 'assistant', 'content': message})

    print(message)

    translate_text(message)

def translate_text(text):
    global is_Speaking

    detect = detect_google(text)
    # tts = translate_google(text, f"{detect}", "JA")
    tts = translate_deeplx(text, f"{detect}", "JA")

    # subtitle = translate_google(text, "ID", "ID")
    try:
        print("Miyu: " + text)
    except Exception as e:
        print("Error!! Text Subtitle : {0}".format(e))
        return

    voicevox_tts(tts)

    generate_subtitle(chat_now, text)

    time.sleep(1)

    is_Speaking = True
    playsound("output.wav")
    is_Speaking = False

    time.sleep(1)
    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)   

def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
        # If the assistant is not speaking, and the chat is not empty, and the chat is not the same as the previous chat
        # then the assistant will answer the chat
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            # Saving chat history
            conversation.append({'role': 'user', 'content': chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)

if __name__ == "__main__":
    mode = input("Mode (1-Mic, 2-Keyboard): ")

    if mode == "1":
        print("Press and Hold Right Shift to record audio")
        while True:
            if keyboard.is_pressed('RIGHT_SHIFT'):
                record_audio()

    elif mode == "2":
        print("Miyu: Halo, OniiChan ada yang bisa miyu bantu?")
        chat = input("")
        hasil = oniichan_name + " said " + chat
        conversation.append({'role': 'user', 'content': hasil})
        openai_answer()
