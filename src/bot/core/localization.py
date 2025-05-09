import json
from pathlib import Path
from string import Template  

locale = "en"  

#TODO: Get back to this module once python 3.14 released

def load_locale(locale_path: Path) -> dict:
    """
    Lload locale for specified language from JSON file.
    
    :param language: language (ex., 'en', 'ru')
    :return: Dictionaly
    """
    locale_path = locale_path.parent / "locales" / f"{locale}.json"
    
    if not locale_path.exists():
        raise FileNotFoundError(f"Locale file for language '{language}' not found.")
    
    with open(locale_path, "r", encoding="utf-8") as file:
        return json.load(file)


def localize_message(locale: dict, message_key: str, **kwargs) -> str:
    """
    Get language-depended string based on key-val pair.
    
    :param locale: Dictionary
    :param message_key: key
    :param kwargs: Args
    :return: Value
    """
    template_str = locale.get(message_key)
    if not template_str:
        raise ValueError(f"Message key '{message_key}' not found in locale.")
        
    return Template(template_str).substitute(**kwargs)

def get_locale():
    return locale