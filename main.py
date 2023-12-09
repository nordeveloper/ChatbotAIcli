import datetime
import requests
import json
from colorama import init, Fore, Back, Style
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
init()

#config speech, language, translate
config = {
    "speech":False,
    "speech_language": "ru",
    "translate": True,
    "speeker":4
}

#model docs and prices https://openrouter.ai/docs#routes
ai_models = [
    'gryphe/mythomax-l2-13b',
    'undi95/toppy-m-7b',
    'gryphe/mythomist-7b',
    'openchat/openchat-7b',
    'nousresearch/nous-capybara-7b',
    'nousresearch/nous-hermes-llama2-13b',
    'open-orca/mistral-7b-openorca',
    'teknium/openhermes-2-mistral-7b',
    'teknium/openhermes-2.5-mistral-7b',
    'huggingfaceh4/zephyr-7b-beta',
    'perplexity/pplx-7b-online',
    'perplexity/pplx-7b-chat',
    'lizpreciatior/lzlv-70b-fp16-hf',
    'mistralai/mistral-7b-instruct',
    'jondurbin/airoboros-l2-70b',
    'nousresearch/nous-hermes-llama2-70b',
    'pygmalionai/mythalion-13b',
    'haotian-liu/llava-13b',      
    'meta-llama/llama-2-13b-chat',
    'meta-llama/llama-2-70b-chat',
    'google/palm-2-chat-bison',
    'meta-llama/codellama-34b-instruct',
    'phind/phind-codellama-34b',
    'google/palm-2-codechat-bison',
    'openai/gpt-3.5-turbo',
    'openai/gpt-3.5-turbo-16k',
    'openai/gpt-4'
    ]


def show_datetime():
    #return datetime.datetime.now()
    today = datetime.datetime.today()
    return today.strftime("%m-%d-%Y %H:%M")
    

def get_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Name: "+ voice.name)


def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 130)
    engine.setProperty('voice', voices[config['speeker']].id)
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Waiting for speech...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        if(audio):
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
        return text

        
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition:{e}")
        return None    


def google_translate(text, dest="ru"):
    translator = Translator() 
    result = translator.translate(text, src="en", dest=dest)
    return result.text   



def getCharacterPrompt(promptjson):
    user_name = ''
    if(promptjson['user_name']):
       user_name = promptjson['user_name']

    sysprompt = promptjson['system_prompt']+"\n"

    if(promptjson['personality']):
        sysprompt+="\nPersonality:"+ promptjson['personality']

    if(promptjson['scenario']):
        sysprompt+="\nScenario:"+ promptjson['scenario']        

    if(promptjson['first_mes']):
        sysprompt+="\nFirst message:"+ promptjson['first_mes']

    sysprompt = sysprompt.replace('{{char}}', promptjson['char_name'])
    sysprompt = sysprompt.replace('{{user}}', user_name)
    return sysprompt


def getAiResponse(prompt):
    apiUrls = [
        'https://api.openai.com/v1/chat/completions',
        'https://openrouter.ai/api/v1/chat/completions'
    ]

    api_url = apiUrls[1]
    f =  open('api_key.txt')
    api_key = f.read()

    conversation.append({"role": "user", "content": prompt})

    myobj = {
        "model": ai_models[18],
        "max_tokens":300,
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
    response = requests.post(api_url, json=myobj, headers=headers)

    aiResponseText = 'Error, try again'

    if response.status_code == 200:
        data = response.json()
        if(data['choices'][0]['message']['content']):
            aiResponseText = data['choices'][0]['message']['content']
            conversation.append({"role": "assistant", "content": aiResponseText})  
        
        return aiResponseText            
    else:
        print("Error: "+ response.status_code + " " + response.text)



conversation = []
system_prompt = ''

charjson = open('character.json')
promptjson = json.load(charjson)

system_prompt = getCharacterPrompt(promptjson)
conversation.append({"role": "system", "content": system_prompt})


def run():
    # get_voices()
    print(f'{Fore.BLUE} Welcome to Chatbot Assistant')
    print(config)

    while True:
        try:
            spokenTxt = speech_to_text()
            inputTxt = input(f'{Fore.BLUE}You: ')                    

            if(inputTxt):
               spoken_text = inputTxt
            elif(spokenTxt):
                spoken_text = spokenTxt
                

            if(spoken_text == 'exit'):
                break

            if(spoken_text == 'date time'):
                datetime = show_datetime()
                print(datetime)
                text_to_speech(datetime)
                continue

            # first_word = spoken_text.split(" ")[0]
            if(len(spoken_text.split()) > 2):
                spoken_text = spoken_text.split(' ', 1)[1]

            AiResponsTxt_en = getAiResponse(spoken_text)
            print(f'{Fore.GREEN}'+AiResponsTxt_en)
            
            if(config['translate']==True):
                AiResponsTxt_ru = google_translate(AiResponsTxt_en)
                print(f'{Fore.YELLOW}'+ AiResponsTxt_ru)
            
                if(config['speech']==True and config['speech_language']=='en'):
                    text_to_speech(AiResponsTxt_en)

                if(config['speech']==True and config['speech_language']=='ru'):
                    text_to_speech(AiResponsTxt_ru)                

        except Exception as e:
            print(e)    



if __name__ == "__main__":
    run()
