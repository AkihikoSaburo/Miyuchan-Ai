import requests
import json
import sys
import googletrans

def translate_deeplx(text, source, target):
    url = "http://localhost:1188/translate"
    headers = {"Content-Type": "application/json"}

    # define the parameters for the translation request
    params = {
        "text": text,
        "source_lang": source,
        "target_lang": target
    }

    payload = json.dumps(params)

    response = requests.post(url, headers=headers, data=payload)
    
    data = response.json()

    translated_text = data['data']

    return translated_text

def detect_google(text):
    translator = googletrans.Translator()
    result = translator.detect(text)
    return result.lang.upper()

# def translate_google(text, source, target):
#     translator = googletrans.Translator()
#     result = translator.translate(text, src=source, dest=target)
#     return result.text

if __name__ == "__main__":
    text = "aku tidak menyukaimu"
    detect = detect_google(text)
    source = translate_deeplx(text, f"{detect}", "JA")
    print(source)