# argos_service.py
import os
import logging
import requests
import sys
from httpx import HTTPStatusError
from typing import Optional
from abc import ABC, abstractmethod
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
from config import ARGOS_BASE_URL

class ArgosTranslationService(PrimaryTranslationService):
    def __init__(self, *, logger = None, timeout: float = 5.0):
        # If no logger passed, use a module‐level logger.
        self.logger = logger or logging.getLogger(__name__)
        base = os.getenv("ARGOS_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
        self.translate_url = f"{base}/translate"
        self.timeout = timeout
        self.service_name = "argos"


    def translate(self, term: str, source_lang: str, target_lang: str) -> Optional[str]:
        payload = {
            "q": term,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
            "alternatives": 0,
        }
        try:
            resp = requests.post(self.translate_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            translated = resp.json()
            return translated.get("translatedText")
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            text = e.response.text if e.response is not None else ""
            if status == 400:
                if "is not supported" in text or "Bad Request" in text:
                    self.logger.warning(
                        f"{self.service_name} unsupported language pair for '{term}' on translation {source_lang} -> {target_lang}\n Exception: {e!r}"
                )
            else:

                self.logger.error(
                    f"{self.service_name} HTTP {status} for '{term}' "
                    f"[{source_lang}→{target_lang}]: {text!r}"
                )
            # Always return None if any error happens.
            return None
        except Exception as e:
            self.logger.critical(
                f"{self.service_name} unexpected error for '{term}' on translation {source_lang} -> {target_lang}\n Exception: {e!r}",
                exc_info=True
            )
        return None


if __name__ == "__main__":
    translator = ArgosTranslationService()
    term = "hello world"
    source_lang = "en"
    target_lang = "de"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")

