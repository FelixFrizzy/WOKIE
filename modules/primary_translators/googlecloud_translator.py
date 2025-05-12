import os
import logging
import sys
from httpx import HTTPStatusError
from google.cloud import translate_v3
from google.api_core.exceptions import GoogleAPICallError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
import argparse
from config import GOOGLE_PROJECT_ID

class GoogleTranslationService(PrimaryTranslationService):
    """
    Translation service that uses the Google Cloud Translation API.
    """
    def __init__(self, *, logger = None):
        # Use the provided project_id or fall back to an environment variable.
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.project_id = GOOGLE_PROJECT_ID 
        self.client = translate_v3.TranslationServiceClient()
        self.parent = f"projects/{self.project_id}/locations/global"
        self.service_name = "google"

    
    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        # Default to "en-US" if source language is not provided. #TODO think about default language. SKOS allows also having no language tag
        src_lang = source_lang if source_lang else "en-US"
        try:
            response = self.client.translate_text(
                contents=[term],
                target_language_code=target_lang,
                parent=self.parent,
                mime_type="text/plain",  
                source_language_code=src_lang,
            )
            if response.translations:
                # Return the first translation result. #TODO can i get synonyms here too?
                #TODO I wonder if only the first word is extracted here. I thought this uses the first phrase / expression but I might be wrong, have to check this
                return response.translations[0].translated_text
        except (GoogleAPICallError) as e:
            msg = str(e)
            if "Source language is invalid" in msg or "Target language is invalid" in msg:
                # Log unsupported language tags as warning
                self.logger.warning(
                    f"{self.service_name} unsupported language pair for '{term}' on translation {source_lang} -> {target_lang}\n Exception: {e!r}"
                )
            else:
                # Log any other exception as error
                self.logger.error(
                    f"{self.service_name} translation failed for '{term}' on translation {source_lang} -> {target_lang}\n Exception: {e!r}",
                    exc_info=True
                )
            # Always return None if any error happens
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

    translator = GoogleTranslationService()
    term = "hello world"
    source_lang = "de"
    target_lang = "zz"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")


