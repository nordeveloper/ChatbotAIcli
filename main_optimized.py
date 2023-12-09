import datetime
import requests
import json
from colorama import init, Fore
from googletrans import Translator
import speech_recognition as sr
import pyttsx3

init()

# Configuration
config = {
    "speech": False,
    "speech_language": "ru",
    "translate": True,
    "speaker": 4
}

# AI models
ai_models = ['gryphe/mythomax-l2-13b', 'undi95/toppy-m-7b']

# Conversation initialization
conversation = []

# Load character prompt from JSON
with open('character.json') as char_json:
    prompt_json = json.load(char_json)

# Build system prompt
system_prompt = prompt_json.get('system_prompt', '') + "\n"
system_prompt += f"\nPersonality: {prompt_json.get('personality', '')}"
system_prompt += f"\nScenario: {prompt_json.get('scenario', '')}"
system_prompt += f"\nFirst message: {prompt_json.get('first_mes', '')}"

system_prompt = system_prompt.replace('{{char}}', prompt_json.get('char_name', ''))
system_prompt = system_prompt.replace('{{user}}', prompt_json.get('user_name', ''))

conversation.append({"role": "system", "content": system_prompt})


def show_datetime():
    today = datetime.datetime.today()
    return today.strftime("%m-%d-%Y %H:%M")


def get_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Name:", voice.name)


def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 130)
    engine.setProperty('voice', voices[config['speaker']].id)
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Waiting for speech...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        if audio:
            print("Recognizing...")
            return recognizer.recognize_google(audio)

    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition: {e}")
    return None


def google_translate(text, dest="ru"):
    translator = Translator()
    result = translator.translate(text, src="en", dest=dest)
    return result.text


def get_ai_response(prompt):
    api_url = 'https://openrouter.ai/api/v1/chat/completions'
    with open('api_key.txt') as f:
        api_key = f.read()

    conversation.append({"role": "user", "content": prompt})

    my_obj = {
        "model": ai_models[1],
        "max_tokens": 300,
        "messages": conversation,
        'temperature': 0.8,
        'top_p': 1,
        'frequency_penalty': 0.8,
        'presence_penalty': 0.8
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost"
    }

    response = requests.post(api_url, json=my_obj, headers=headers)

    ai_response_text = 'Error, try again'

    if response.status_code == 200:
        data = response.json()
        ai_response_text = data['choices'][0]['message']['content']
        conversation.append({"role": "assistant", "content": ai_response_text})

    else:
        print(f"Error: {response.status_code} {response.text}")

    return ai_response_text


def run():
    print(f'{Fore.BLUE} Welcome to Chatbot Assistant')
    print(config)

    while True:
        try:
            spoken_text = speech_to_text() or input(f'{Fore.BLUE}You: ')

            if spoken_text.lower() == 'exit':
                break

            if spoken_text.lower() == 'date time':
                current_datetime = show_datetime()
                print(current_datetime)
                text_to_speech(current_datetime)
                continue

            if len(spoken_text.split()) > 2:
                spoken_text = spoken_text.split(' ', 1)[1]

            ai_response_en = get_ai_response(spoken_text)
            print(f'{Fore.GREEN}' + ai_response_en)

            if config['translate']:
                ai_response_ru = google_translate(ai_response_en)
                print(f'{Fore.YELLOW}' + ai_response_ru)

                if config['speech'] and config['speech_language'] == 'en':
                    text_to_speech(ai_response_en)

                if config['speech'] and config['speech_language'] == 'ru':
                    text_to_speech(ai_response_ru)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    run()
