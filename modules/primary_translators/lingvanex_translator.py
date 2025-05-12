import logging
import translators
import sys
from httpx import HTTPStatusError
from translators.server import TranslatorError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService



class LingvanexTranslationService(PrimaryTranslationService):
    def __init__(self, *, logger = None):
        # If no logger passed, use a module‐level logger
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.service_name = "lingvanex"

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        lang_mapping = {
        'ar': 'ar_EG',
        'de': 'de_DE',
        'en': 'en_US',
        'es': 'es_ES',
        'fr': 'fr_FR',
        'hr': 'hr_HR',
        'hu': 'hu_HU',
        'it': 'it_IT',
        'la': 'la_VAT',
        'nl': 'nl_NL',
        'pt': 'pt_PT',
        'ru': 'ru_RU',
        'sl': 'sl_SI',
        'sr': 'sr-Cyrl_RS',
        'el': 'el_GR', 
        'uk': 'uk_UA'
        }
        try:
            translated = translators.translate_text(term, translator="lingvanex", from_language=lang_mapping[source_lang], to_language=lang_mapping[target_lang])
            # in case someone passes "is_detail_result=True", the result is a dict
            if isinstance(translated, dict):
                return translated.get("result")
            return(translated)
        
        except (KeyError, TranslatorError) as e:
            msg = str(e)
            print("msg")
            print(msg)
            if source_lang in msg or target_lang in msg:
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

    translator = LingvanexTranslationService()
    term = "hello world"
    source_lang = "el"
    target_lang = "uk"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")
