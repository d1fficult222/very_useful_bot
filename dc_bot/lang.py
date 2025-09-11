import json
import settings

try:
    with open(f"assets/lang/{settings.LANG}.json", 'r', encoding="UTF-8") as f:
        lang = json.load(f)
except FileNotFoundError:
    with open(f"assets/lang/zh_TW.json", 'r', encoding="UTF-8") as f:
        lang = json.load(f)

def text(id: str, *args) -> str:
    """
    returns lang[id].format(*args)\n
    returns id if id is not found or the number of arguments is not correct
    """
    if id in lang:
        if args:
            try:
                return lang[id].format(*args)
            except IndexError:
                return id
        else:
            return lang[id]
    else:
        return id
