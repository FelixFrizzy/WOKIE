import logging
import sys
from httpx import HTTPStatusError
from deep_translator import PonsTranslator
from deep_translator.exceptions import LanguageNotSupportedException
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService

class PonsTranslationService(PrimaryTranslationService):
    def __init__(self, *, logger = None):
        # If no logger passed, use a module‐level logger
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.service_name = "pons"

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        try:
            pons_translator = PonsTranslator(source=source_lang, target=target_lang)
            translated = pons_translator.translate(term)
            # in case someone passes "return_all=True" to the class, the result is a list
            if isinstance(translated, list):
                return translated[0]

            return translated
        except LanguageNotSupportedException as e:
            msg = str(e)
            if "Unsupported from_language" in msg or "Unsupported to_language" in msg:
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

    translator = PonsTranslationService()
    term = "hello world"
    source_lang = "en"
    target_lang = "de"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")

