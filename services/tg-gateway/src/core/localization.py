"""
file: services/tg-gateway/src/core/localization.py

Localization service for providing multilingual text support.

This module defines the `Localize` class, which handles loading and accessing
localized string resources from JSON files. It is designed to be instantiated
once and passed to handlers via dependency injection.
"""

import json
from pathlib import Path
from string import Template
from typing import Any, Dict

# Define the root path for locale files relative to this file.
# src/core/localization.py -> src/
LOCALES_ROOT = Path(__file__).resolve().parent.parent


class Localize:
    """
    A service for handling string localization from JSON files.

    This class loads all available locale files from the feature directories
    into memory upon initialization, providing a simple `get` method to
    retrieve and format strings for a specific language.

    Attributes:
        locales (Dict[str, Dict[str, str]]): A dictionary caching all loaded
                                             locale data, keyed by language code.
        default_lang (str): The default language to use if a key is not found
                            in the requested language.
    """

    def __init__(self, default_lang: str = "en"):
        """
        Initializes the localization service and loads all locales.

        Args:
            default_lang (str): The default language code (e.g., "en").
        """
        self.locales: Dict[str, Dict[str, str]] = {}
        self.default_lang = default_lang
        self._load_all_locales()

    def _load_all_locales(self) -> None:
        """
        Scans all feature directories for 'locales/*.json' files and loads them.
        """
        features_path = LOCALES_ROOT / "bot" / "features"
        if not features_path.is_dir():
            return

        for locale_file in features_path.glob("**/locales/*.json"):
            # The language code is the filename without extension (e.g., "en").
            lang_code = locale_file.stem

            if lang_code not in self.locales:
                self.locales[lang_code] = {}

            with open(locale_file, "r", encoding="utf-8") as f:
                # Merge dictionaries, allowing features to have their own locale files.
                self.locales[lang_code].update(json.load(f))

    def get(self, key: str, lang: str | None = None, **kwargs: Any) -> str:
        """
        Retrieves and formats a localized string for a given key.

        It first tries to find the key in the specified language, then falls back
        to the default language if the key is not found.

        Args:
            key (str): The key of the string to retrieve (e.g., "start_welcome_message").
            lang (str, optional): The language code to use. Defaults to the service's
                                  default language.
            **kwargs: Keyword arguments to substitute into the string template.

        Returns:
            str: The final, formatted string.

        Raises:
            KeyError: If the key is not found in either the requested or
                      default locale.
        """
        lang_to_use = lang or self.default_lang

        # Get the template string, falling back to the default language.
        template_str = self.locales.get(lang_to_use, {}).get(key)
        if template_str is None and lang_to_use != self.default_lang:
            template_str = self.locales.get(self.default_lang, {}).get(key)

        if template_str is None:
            raise KeyError(
                f"Localization key '{key}' not found in '{lang_to_use}' "
                f"or default locale '{self.default_lang}'."
            )

        # Substitute placeholders if any are provided.
        if kwargs:
            return Template(template_str).substitute(**kwargs)

        return template_str
