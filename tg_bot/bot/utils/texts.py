import json
import os

def get_text(key) -> str:
    f = open('bot/utils/texts.json')
    data = json.load(f)
    return data.get(key, None)