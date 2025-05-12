import logging
import requests
import sys
from httpx import HTTPStatusError
from requests.exceptions import Timeout, RequestException
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
from config import PONS_API_KEY

class PonsPaidTranslationService(PrimaryTranslationService):
    def __init__(self, *, logger=None):
        self.base_url = "https://translate-api.pons.com/v1/translate"
        # If no logger passed, use a module‐level logger
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.service_name = "ponspaid"

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:

        langs_allowed = ["ar", "no", "bg", "ca", "zh", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "hi", "hu", "ga", "it", "ja", "ko", "lv", "lt", "nn", "pl", "pt", "ro", "ru", "sk", "sl", "es", "sv", "tr", "uk"]
        if source_lang not in langs_allowed or target_lang not in langs_allowed:
            self.logger.warning(
                    f"{self.service_name} unsupported language pair for '{term}' on translation {source_lang} -> {target_lang}\n"
                )
            return None

        # # Pons in general only allows latin in combination with german
        # # Seems like latin is not implemented in the API
        # if "la" in (source_lang, target_lang) and {source_lang, target_lang} != {"la", "de"}:
        #     self.logger.warning(
        #         f"{self.service_name} only allows latin in combination with german: failed on '{term}' on translation {source_lang} -> {target_lang}\n "
        #     )
        #     return None

        headers = {
            "Accept": "application/json",
            "X-PONS-APIKEY": PONS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
            "segments": [
                {"text": term}
            ]
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout = 2)
            response.raise_for_status()
            data = response.json()

            # the translated text should be in segments[0].text
        
            return data["segments"][0]["text"]
        
        except Timeout:
            self.logger.warning(f"{self.service_name} request timed out for '{term}' from {source_lang} to {target_lang}")
            return None
    
        except HTTPStatusError as e:
            code = e.response.status_code
            if code == 429:
                self.logger.critical(
                    f"{self.service_name} returned Too Many Requests – rate limit reached, exiting."
                )
                sys.exit(1)
            else:
                self.logger.critical(
                    f"{self.service_name} returned HTTP {code}: {e.response.text!r}"
                )
                # re-raise
                raise

        except Exception as e:
            # anything else logged as critical
            self.logger.critical(
                f"{self.service_name} unexpected error for '{term}' on translation {source_lang} -> {target_lang}\n Exception: {e!r}",
                exc_info=True
            )
            return None

    
if __name__ == "__main__":

    translator = PonsPaidTranslationService()
    term = "hello world"
    source_lang = "en"
    target_lang = "uk"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")

